import logging

import requests
import json


class AppStoreManager:
    def __init__(self, country="us", use_sandbox=True):
        self.country = country
        self.use_sandbox = use_sandbox
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.handler = logging.StreamHandler()
        self.handler.setLevel(logging.INFO)
        self.logger.addHandler(self.handler)

    def retrieve_product_info(self, bundle_id):
        if self.use_sandbox:
            url = f"https://sandbox.itunes.apple.com/lookup?country={self.country}&id={bundle_id}"
        else:
            url = (
                f"https://itunes.apple.com/lookup?country={self.country}&id={bundle_id}"
            )
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = json.loads(response.content)
            if data.get("resultCount") > 0:
                products = data.get("results")
                return products[0]
            else:
                self.logger.info(f"No products found for bundle ID '{bundle_id}'.")
        except requests.exceptions.HTTPError as e:
            self.logger.error(
                f"Error retrieving product data for bundle ID '{bundle_id}': {e}"
            )
        except Exception as e:
            self.logger.error(
                f"An error occurred retrieving product data for bundle ID '{bundle_id}': {e}"
            )

    def get_app_name(self, bundle_id):
        product = self.retrieve_product_info(bundle_id)
        return product.get("trackName") if product else None

    def get_app_version(self, bundle_id):
        product = self.retrieve_product_info(bundle_id)
        return product.get("version") if product else None

    def get_app_price(self, bundle_id):
        product = self.retrieve_product_info(bundle_id)
        return product.get("price") if product else None

    def get_app_description(self, bundle_id):
        product = self.retrieve_product_info(bundle_id)
        return product.get("description") if product else None


def call():
    app_store_manager = AppStoreManager(country="us")

    bundle_id = "com.grahm.mac.genchat.weekly"
    app_name = app_store_manager.get_app_name(bundle_id)
    app_version = app_store_manager.get_app_version(bundle_id)
    app_price = app_store_manager.get_app_price(bundle_id)
    app_description = app_store_manager.get_app_description(bundle_id)

    print(f"App Name: {app_name}")
    print(f"App Version: {app_version}")
    print(f"App Price: {app_price}")
    print(f"App Description: {app_description}")
