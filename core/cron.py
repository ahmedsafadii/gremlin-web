import json
from datetime import datetime
import kronos
import jwt
from django.core.exceptions import ObjectDoesNotExist
from api.v1.user.serializer import UserSerializer
from core.models import UserPlan, Plan
from core.models.app import AppleWebHook
from core.models.user import UserTransaction
from gremlin.middleware import catch_custom_exception
from utils.appstore import SubscriptionStatus
from django.utils import timezone


@kronos.register("* * * * *")
def check_subscription_validate():
    try:
        users_plans = UserPlan.objects.filter(expire_in__lt=timezone.now())
        users_plans.update(is_active=False)
        for user_plan in users_plans:
            balance = (
                UserSerializer(user_plan.user).data.get("balance", {}).get("balance", 0)
            )
            UserTransaction.objects.create_transaction(
                user=user_plan.user,
                amount=balance,
                is_credit=False,
                notes=f"Tokens Expired for transaction {user_plan.original_transaction_id}",
                original_transaction_id=user_plan.original_transaction_id,
            )
    except ObjectDoesNotExist as e:
        catch_custom_exception(e)


@kronos.register("* * * * *")
def check_apple_webhook(hook_id=None):
    try:
        hooks = AppleWebHook.objects.filter(is_processed=False)
        if hook_id:
            hooks = hooks.filter(id=hook_id)
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
                    notification_type = signed_payload.get("notificationType")
                    sub_type = signed_payload.get("subtype", "")

                    originalTransactionId = signed_transaction_info.get(
                        "originalTransactionId"
                    )
                    signed_payload["data"][
                        "signedTransactionInfo"
                    ] = signed_transaction_info
                    signed_payload["data"]["signedRenewalInfo"] = signed_renewal_info
                    hook.notification_type = notification_type
                    hook.notification_subtype = sub_type
                    hook.original_transaction_id = originalTransactionId
                    hook.json_processed = json.dumps(signed_payload, indent=4)
                    hook.is_processed = True
                    hook.save()
                else:
                    print(
                        "Notify: signed_transaction_info or signed_renewal_info is missing"
                    )
            else:
                print("Notify: the signed_payload is wrong")
    except (Exception,) as e:
        catch_custom_exception(e)


def decode_jwt(token):
    return jwt.decode(token)


def check_status(signed_payload, signed_transaction_info, signed_renewal_info):
    # Payload
    notification_type = signed_payload.get("notificationType", "")
    sub_type = signed_payload.get("subtype", "")

    # Transaction info
    originalTransactionId = signed_transaction_info.get("originalTransactionId")
    productId = signed_transaction_info.get("productId")

    expiration_date_ms = signed_transaction_info.get("expiresDate")
    expiration_date = datetime.fromtimestamp(int(expiration_date_ms) / 1000)

    try:
        plan = Plan.objects.get(bundle_id=productId)
        user_plan = UserPlan.objects.filter(
            original_transaction_id=originalTransactionId
        )
        for user_p in user_plan:
            is_active, user_plan_type = check_notification_type(
                expiration_date=expiration_date,
                notification_type=notification_type,
                notification_sub_type=sub_type,
                signed_renewal_info=signed_renewal_info,
                user_plan=user_p,
            )
            user_p.plan = plan
            user_p.expire_in = expiration_date
            user_p.is_active = is_active
            user_p.type = user_plan_type
            user_p.save()
    except (Exception,) as e:
        catch_custom_exception(e)


def check_notification_type(
    expiration_date,
    notification_type,
    notification_sub_type,
    signed_renewal_info,
    user_plan,
):

    if expiration_date < datetime.now():
        return False, SubscriptionStatus.EXPIRED.value

    if notification_type in [
        "AUTO_RENEW_ENABLED",
        "DID_CHANGE_RENEWAL_PREF",
        "DID_CHANGE_RENEWAL_STATUS",
        "DID_RENEW",
        "SUBSCRIBED",
    ]:
        auto_renew_status = bool(signed_renewal_info.get("autoRenewStatus"))
        if auto_renew_status:
            if notification_type == "DID_RENEW" or notification_sub_type in [
                "INITIAL_BUY",
                "RESUBSCRIBE",
                "DOWNGRADE",
                "UPGRADE",
            ]:
                balance = (
                    UserSerializer(user_plan.user)
                    .data.get("balance", {})
                    .get("balance", 0)
                )

                if balance != user_plan.plan.tokens:
                    plan_tokens = user_plan.plan.tokens - balance
                    UserTransaction.objects.create_transaction(
                        user=user_plan.user,
                        amount=plan_tokens,
                        is_credit=True,
                        is_gift=False,
                        is_free=False,
                        notes=f"Reset tokens for {user_plan.original_transaction_id}",
                        original_transaction_id=user_plan.original_transaction_id,
                    )

            return True, SubscriptionStatus.VALID.value
        else:
            return False, SubscriptionStatus.NOT_VALID.value

    return False, SubscriptionStatus.NOT_VALID.value

    # AUTO_RENEW_ENABLED - Then check - signed_renewal_info to key autoRenewStatus - is_active = True
    # AUTO_RENEW_DISABLED - Then check - signed_renewal_info to key autoRenewStatus -  is_active = False
    # DID_CHANGE_RENEWAL_PREF (UPGRADE) - then check - signed_renewal_info to key autoRenewStatus and product id = True
    # SUBSCRIBED (INITIAL_BUY) - then check - signed_renewal_info to key autoRenewStatus is_active = True
    # DID_RENEW - then check - signed_renewal_info to key autoRenewStatus is_active = True
    # SUBSCRIBED (RESUBSCRIBE) --
