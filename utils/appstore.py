import requests
from datetime import datetime
from enum import Enum
from gremlin.settings_dev import IAP_PASSWORD, DEBUG


class SubscriptionStatus(Enum):
    VALID = "valid"
    TRIAL = "trial"
    EXPIRED = "expired"
    NOT_VALID = "not_valid"


class SubscriptionManager:
    def __init__(self):
        self.password = IAP_PASSWORD
        if DEBUG:
            self.url = "https://sandbox.itunes.apple.com/verifyReceipt"
        else:
            # self.url = "https://sandbox.itunes.apple.com/verifyReceipt"
            self.url = "https://buy.itunes.apple.com/verifyReceipt"

    def validate_receipt(self, receipt_data):

        response = requests.post(
            self.url, json={"receipt-data": receipt_data, "password": self.password}
        )
        data = response.json()
        result = {
            "status": SubscriptionStatus.NOT_VALID,
            "latest_receipt_info": None,
            "expiration_date_ms": None,
            "expiration_date": None,
            "bundle_id": None,
        }
        if data["status"] == 0:
            latest_receipt_info = data["latest_receipt_info"]
            original_transaction_id = latest_receipt_info[0]["original_transaction_id"]
            product_id = latest_receipt_info[0]["product_id"]
            expiration_date_ms = latest_receipt_info[0]["expires_date_ms"]
            expiration_date = datetime.fromtimestamp(int(expiration_date_ms) / 1000)
            result["latest_receipt_info"] = latest_receipt_info
            result["expiration_date_ms"] = expiration_date_ms
            result["expiration_date"] = expiration_date
            result["product_id"] = product_id
            result["original_transaction_id"] = original_transaction_id

            # Check if the subscription is expired
            if expiration_date < datetime.now():
                result["status"] = SubscriptionStatus.EXPIRED
                return result

            # Check if the subscription is a free trial
            if latest_receipt_info[0]["is_trial_period"] == "true":
                result["status"] = SubscriptionStatus.TRIAL
                return result

            # The subscription is valid
            result["status"] = SubscriptionStatus.VALID
            return result
        else:
            result["status"] = SubscriptionStatus.NOT_VALID
            return result
