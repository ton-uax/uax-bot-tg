import typing

from . import models as account_models


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
        return new_user

