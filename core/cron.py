import json
from datetime import datetime
import kronos
import jwt
from django.core.exceptions import ObjectDoesNotExist

from core.models import UserPlan, Plan
from core.models.app import AppleWebHook
from utils.appstore import SubscriptionStatus
from django.utils import timezone


@kronos.register("* * * * *")
def check_subscription_validate():
    try:
        UserPlan.objects.filter(expire_in__lt=timezone.now()).update(is_active=False)
    except ObjectDoesNotExist as e:
        print(f"Notify: there is error in cronjob {str(e)}")


@kronos.register("* * * * *")
def check_apple_webhook():
    try:
        hooks = AppleWebHook.objects.filter(is_processed=False)
        for hook in hooks:
            post_body = json.loads(hook.post_body)
            signed_payload = post_body.get("signedPayload", None)
            if signed_payload:
                signed_payload = jwt.decode(
                    signed_payload, options={"verify_signature": False}
                )

                signed_transaction_info = signed_payload.get("data", {}).get(
                    "signedTransactionInfo", None
                )

                signed_renewal_info = signed_payload.get("data", {}).get(
                    "signedRenewalInfo", None
                )

                if signed_transaction_info and signed_renewal_info:
                    signed_transaction_info = jwt.decode(
                        signed_transaction_info, options={"verify_signature": False}
                    )
                    signed_renewal_info = jwt.decode(
                        signed_renewal_info, options={"verify_signature": False}
                    )
                    check_status(
                        signed_payload, signed_transaction_info, signed_renewal_info
                    )
                    hook.is_processed = True
                    hook.save()
                else:
                    print(
                        "Notify: signed_transaction_info or signed_renewal_info is missing"
                    )
            else:
                print("Notify: the signed_payload is wrong")
    except (Exception,) as e:
        print(f"Notify: there is error in cronjob {str(e)}")


def decode_jwt(token):
    return jwt.decode(token)


def check_status(signed_payload, signed_transaction_info, signed_renewal_info):
    # Payload
    notification_type = signed_payload.get("notificationType")

    # Transaction info
    originalTransactionId = signed_transaction_info.get("originalTransactionId")
    productId = signed_transaction_info.get("productId")

    expiration_date_ms = signed_transaction_info.get("expiresDate")
    expiration_date = datetime.fromtimestamp(int(expiration_date_ms) / 1000)
    print(originalTransactionId)
    try:
        plan = Plan.objects.get(bundle_id=productId)
        user_plan = UserPlan.objects.get(original_transaction_id=originalTransactionId)
        is_active, user_plan_type = check_notification_type(
            expiration_date=expiration_date,
            notification_type=notification_type,
            signed_renewal_info=signed_renewal_info,
        )
        user_plan.plan = plan
        user_plan.expire_in = expiration_date
        user_plan.is_active = is_active
        user_plan.type = user_plan_type
        user_plan.save()
    except (Exception,) as e:
        print(f"Notify: there is error in cronjob {str(e)}")


def check_notification_type(expiration_date, notification_type, signed_renewal_info):

    if expiration_date < datetime.now():
        return False, SubscriptionStatus.EXPIRED.value
    print(notification_type)
    if notification_type in [
        "AUTO_RENEW_ENABLED",
        "DID_CHANGE_RENEWAL_PREF",
        "DID_CHANGE_RENEWAL_STATUS",
        "SUBSCRIBED",
        "DID_RENEW",
        "SUBSCRIBED",
    ]:
        auto_renew_status = bool(signed_renewal_info.get("autoRenewStatus"))
        if auto_renew_status:
            return True, SubscriptionStatus.VALID.value
        else:
            return False, SubscriptionStatus.NOT_VALID.value

    return False, SubscriptionStatus.NOT_VALID.value

    # AUTO_RENEW_ENABLED - Then check - signed_renewal_info to key autoRenewStatus - is_active = True
    # AUTO_RENEW_DISABLED - Then check - signed_renewal_info to key autoRenewStatus -  is_active = False
    # DID_CHANGE_RENEWAL_PREF (UPGRADE) - then check - signed_renewal_info to key autoRenewStatus and product id = True
    # SUBSCRIBED (INITIAL_BUY) - then check - signed_renewal_info to key autoRenewStatus is_active = True
    # DID_RENEW - then check - signed_renewal_info to key autoRenewStatus is_active = True
    # SUBSCRIBED (RESUBSCRIBE)
