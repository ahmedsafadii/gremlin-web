# helpers.py
import os
import uuid
import jwt
from datetime import timedelta
from django.utils.deconstruct import deconstructible
from django.utils import timezone
from gremlin.settings_dev import APP_KEY_ID, APP_TEAM_ID, APP_BUNDLE_ID


@deconstructible
class RandomFileName(object):
    def __init__(self, path):
        self.path = os.path.join(path, "%s%s")

    def __call__(self, _, filename):
        extension = os.path.splitext(filename)[1]
        return self.path % (uuid.uuid1(), extension)


def get_apple_user():
    headers = {"kid": APP_KEY_ID}

    payload = {
        "iss": APP_TEAM_ID,
        "iat": timezone.now(),
        "exp": timezone.now() + timedelta(days=180),
        "aud": "https://appleid.apple.com",
        "sub": APP_BUNDLE_ID,
    }

    key_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "utils/keys/AuthKey_Y6AK8K79V7.p8"
    )

    with open(key_path, "r+b") as keyfile:
        secret = keyfile.read()
        client_secret = jwt.encode(payload, secret, algorithm="ES256", headers=headers)
        return APP_BUNDLE_ID, client_secret


def get_setting_value(key):
    from core.models import Setting

    try:
        return Setting.objects.get(key=key).value
    except Setting.DoesNotExist:
        return ""


# def get_user_balance(user_id):
#     from core.models import UserPlan, Bot
#
#     credit = 0
#
#     user_plans = UserPlan.objects.filter(user_id=user_id).exclude(plan__is_unlimited=True)
#     debit = Bot.objects.filter(user_id=user_id, user__plans__expire_in__isnull=True).aggregate(
#         Sum("total_answer_words")
#     )["total_answer_words__sum"] or 0
#
#     if len(user_plans) > 0:
#         credit = sum(user_plan.plan.words for user_plan in user_plans if not user_plan.plan.is_unlimited)
#
#     return {"credit": int(credit), "debit": int(debit), "balance": int(credit - debit) if int(credit - debit) >= 0 else 0}
