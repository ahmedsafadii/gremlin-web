# helpers.py
import os
import time
import uuid
import jwt
from datetime import timedelta, datetime
from django.utils.deconstruct import deconstructible
from django.utils import timezone
import requests
from gremlin.settings_dev import APP_KEY_ID, APP_TEAM_ID, APP_BUNDLE_ID
import hashlib


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
        os.path.dirname(os.path.dirname(__file__)), "utils/keys/AuthKey_TV7554QL5R.p8"
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


class UserColorGenerator:
    @staticmethod
    def generate_user_color(user_id):
        # Hash the user ID using SHA256 to get a unique hash value
        hash_val = hashlib.sha256(str(user_id).encode()).hexdigest()

        # Use the last 6 characters of the hash value as the color code
        color_code = hash_val[-6:]

        # If the generated color code starts with a letter, add a 0 in front to ensure it is a valid hex code
        if color_code[0] in ["a", "b", "c", "d", "e", "f"]:
            color_code = "0" + color_code[1:]

        # Modify the color code to make it darker
        color_code = UserColorGenerator.darken_color(color_code)

        # Return the color code with a '#' in front to indicate it is a hex code
        return color_code

    @staticmethod
    def darken_color(color_code):
        # Convert the hex color code to RGB values
        r = int(color_code[0:2], 16)
        g = int(color_code[2:4], 16)
        b = int(color_code[4:6], 16)

        # Darken the color by 30%
        r = max(0, int(r * 0.7))
        g = max(0, int(g * 0.7))
        b = max(0, int(b * 0.7))

        # Convert the new RGB values back to hex format
        return "{:02x}{:02x}{:02x}".format(r, g, b)


def testAppStoreJWT():

    headers = {"kid": "357Q2LDNYU", "typ": "JWT"}

    token_gen_date = datetime.now()
    exp = int(time.mktime((token_gen_date + timedelta(minutes=20)).timetuple()))

    payload = {
        "iss": "53936e5d-425f-477c-b35e-3a0307bd645e",
        "exp": exp,
        "aud": "appstoreconnect-v1",
    }
    print(payload)

    key_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "utils/keys/AppStore_357Q2LDNYU.p8"
    )

    with open(key_path, "r+b") as keyfile:
        secret = keyfile.read()
        client_secret = jwt.encode(
            payload, secret, algorithm="ES256", headers=headers
        ).decode("utf-8")
        print("Bearer", client_secret)


def testStoreKit():
    headers = {"kid": "357Q2LDNYU", "typ": "JWT"}

    token_gen_date = datetime.now()
    exp = int(time.mktime((token_gen_date + timedelta(minutes=20)).timetuple()))

    payload = {
        "iss": "53936e5d-425f-477c-b35e-3a0307bd645e",
        "exp": exp,
        "aud": "appstoreconnect-v1",
        "bid": APP_BUNDLE_ID,
    }
    print(payload)

    key_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "utils/keys/AppStore_357Q2LDNYU.p8",
    )

    with open(key_path, "r+b") as keyfile:
        secret = keyfile.read()
        client_secret = jwt.encode(
            payload, secret, algorithm="ES256", headers=headers
        ).decode("utf-8")

        url = "https://api.storekit-sandbox.itunes.apple.com/inApps/v1/subscriptions/2000000291031441"
        headers = {
            "Authorization": f"Bearer {client_secret}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        print(data)

        # decoded1 = jwt.decode(
        #     data["data"][0]["lastTransactions"][0]["signedTransactionInfo"],
        #     options={"verify_signature": False},
        # )
        #
        # decoded2 = jwt.decode(
        #     data["data"][0]["lastTransactions"][0]["signedRenewalInfo"],
        #     options={"verify_signature": False},
        # )

        # most_recent = None
        # for test in data.get("signedTransactions"):
        #     decoded = jwt.decode(test, options={"verify_signature": False})
        #     expires_date = decoded.get("expiresDate")
        #     if most_recent is None or expires_date > most_recent:
        #         most_recent = expires_date
        #         print(decoded)
        # print(most_recent)
        # test
