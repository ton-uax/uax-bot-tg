from pyrogram import User
import requests


class WalletAPI:
    base_url = 'http://uax-api:8080/api/v1/'

    @classmethod
    def registration_user(cls, tg_user: User):
        request_url = "accounts/user/"

        username = tg_user.username
        first_name = tg_user.first_name
        last_name = tg_user.last_name

        if not username:
            username = "[отсутствует]"
        if not first_name:
            first_name = "[отсутствует]"
        if not last_name:
            last_name = "[отсутствует]"

        data = {
            "tg_id": tg_user.id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
        }

        response = requests.post(cls.base_url + request_url, data=data)

        if response.status_code == 201:
            return "is_created"

    @classmethod
    def create_wallet(cls, tg_id: int):
        request_url = f'wallet/create/{tg_id}/'
        response = requests.get(cls.base_url + request_url)
        return response.json()

    @classmethod
    def check_user(cls, tg_id: int):
        request_url = f'accounts/{tg_id}/'
        response = requests.get(cls.base_url+request_url)
        return response

    @classmethod
    def check_wallet(cls, address: str):
        request_url = f'wallet/check/{address}/'
        response = requests.get(cls.base_url + request_url)
        if response.status_code == 200:
            return True

    @classmethod
    def send_tx(cls, sender_id, address_to: str, amount: str):
        request_url = f'wallet/sendTx/'
        data = {
            "sender_id": sender_id,
            "address_to": address_to,
            "amount": amount
        }
        response = requests.post(cls.base_url + request_url, data=data)

    @classmethod
    def activate_wallet(cls, wallet_id):
        request_url = f'wallet/activate/{wallet_id}/'
        response = requests.get(cls.base_url + request_url)

    @classmethod
    def edit_title(cls, wallet_id, title):
        request_url = f'wallet/editTitle/'
        data = {
            "id": wallet_id,
            "title": title
        }
        response = requests.post(cls.base_url + request_url, data=data)

