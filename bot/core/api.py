from pyrogram import User
import requests


class WalletAPI:
    base_url = 'http://uax-api:8080/api/v1/'

    @classmethod
    def registration_user(cls, tg_user: User, iphone: bool):
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
            "last_name": last_name
        }

        response = requests.post(cls.base_url + request_url, data=data)

        if response.status_code == 201:
            return "is_created"

    @classmethod
    def check_user(cls, tg_id: int):

        request_url = f'accounts/{tg_id}/'
        response = requests.get(cls.base_url+request_url)
        return response


