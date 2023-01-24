import requests
import configparser
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from enum import Enum


class EbayHeaders(Enum):
    COMPATIBILITY_LEVEL = 'X-EBAY-API-COMPATIBILITY-LEVEL'
    DEV_NAME = 'X-EBAY-API-DEV-NAME'
    APP_NAME = 'X-EBAY-API-APP-NAME'
    CERT_NAME = 'X-EBAY-API-CERT-NAME'
    CALL_NAME = 'X-EBAY-API-CALL-NAME'
    SITE_ID = 'X-EBAY-API-SITEID'
    CONTENT_TYPE = 'Content-Type'


class EbayApi:
    def __init__(self, endpoint: str, auth_token: str, compatibility_level: str, dev_name: str, app_name: str,
                 cert_name: str):
        self.endpoint = endpoint
        self.headers = {
            EbayHeaders.COMPATIBILITY_LEVEL.value: compatibility_level,
            EbayHeaders.DEV_NAME.value: dev_name,
            EbayHeaders.APP_NAME.value: app_name,
            EbayHeaders.CERT_NAME.value: cert_name,
            EbayHeaders.CALL_NAME.value: 'PlaceOffer',
            EbayHeaders.SITE_ID.value: '0',
            EbayHeaders.CONTENT_TYPE.value: 'text/xml'
        }
        self.headers['RequesterCredentials'] = {
            'eBayAuthToken': auth_token
        }

    def place_offer(self, item_id: str, amount: float, quantity: int):
        payload = f'''
        <PlaceOfferRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <RequesterCredentials>
                <eBayAuthToken>{self.headers['RequesterCredentials']['eBayAuthToken']}</eBayAuthToken>
            </RequesterCredentials>
            <Offer>
                <ItemID>{item_id}</ItemID>
                <MaxBid>{amount}</MaxBid>
                <Quantity>{quantity}</Quantity>
            </Offer>
            <BlockOnWarning>true</BlockOnWarning>
        </PlaceOfferRequest>
        '''
        response = requests.post(self.endpoint, headers=self.headers, data=payload)
        return response


def validate_input(input_str: str, input_type: type):
    try:
        return input_type(input_str)
    except ValueError:
        raise ValueError(f"Invalid {input_type}")


def schedule_bid(api: EbayApi, item_id: str, amount: float, quantity: int, bid_time: str):
    scheduler = BlockingScheduler()
    scheduler.add_job(api.place_offer, 'date', run_date=bid_time, args=[item_id, amount, quantity])
    scheduler.start()


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')

    endpoint = 'https://api.ebay.com/ws/api.dll'
    auth_token = config['DEFAULT']['auth_token']
    compatibility_level = config['DEFAULT']['compatibility_level']
    dev_name = config['DEFAULT']['dev_name']
    app_name = config['DEFAULT']['app_name']
    cert_name = config['DEFAULT']['cert_name']

    api = EbayApi(endpoint, auth_token, compatibility_level, dev_name, app_name, cert_name)

    item_id = input("Enter the item ID: ")
    amount = validate_input(input("Enter the bid amount: "), float)
    quantity = validate_input(input("Enter the quantity: "), int)
    bid_time = input("Enter the time at which the bid will be made (YYYY-MM-DD HH:MM:SS): ")
    bid_time = datetime.strptime(bid_time, "%Y-%m-%d %H:%M:%S")

    schedule_bid(api, item_id, amount, quantity, bid_time)
