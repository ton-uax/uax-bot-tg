import typing

from core.apps.account import models as account_models
from django.core.cache import cache


def register_user(*, tg_id: int,
                  username: str,
                  first_name: str,
                  last_name: str
                  ) -> typing.Optional["account_models.TelegramAccount"]:
    if not account_models.TelegramAccount.objects.filter(tg_id=tg_id).exists():
        new_user = account_models.TelegramAccount.objects.create(
            tg_id=tg_id,
            username=username,
            last_name=last_name,
            first_name=first_name)

        cache_user(new_user)
        return new_user


def cache_user(account: "account_models.TelegramAccount"):
    users = cache.get("users", {})

    users[account.tg_id] = dict(
        id=account.id,
        tg_id=account.tg_id,
        username=account.username,
        first_name=account.first_name,
        last_name=account.last_name,

    )

    cache.set("users", users, timeout=None)
    cache.set(f"flags:{account.tg_id}", {
        "await_to_amount": False,
        "await_to_address": False,
        "await_wallet_title": False,
        "await_mnemonic": False}, timeout=None)
    cache.set(f"wallets:{account.tg_id}", {}, timeout=None)
    cache.set(f"cache:{account.tg_id}", {
        "address_to": str,
        "last_msg_id": int
    }, timeout=None)
