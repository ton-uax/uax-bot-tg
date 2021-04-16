from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _

from core.apps.common import models as common_models


class TelegramAccount(common_models.BaseModel):
    tg_id = models.PositiveIntegerField(_("Телеграм юзер ID"), unique=True)
    username = models.CharField(_("Юзернейм"), max_length=255, default=' ')
    first_name = models.CharField(_("Имя"), max_length=255, default=' ')
    last_name = models.CharField(_("Фамилия"), max_length=255, default=' ')

    class Meta:
        verbose_name = 'Телеграм пользователя'
        verbose_name_plural = 'Телеграм пользователи'

    def __str__(self):
        return f"{self.tg_id} ({self.username})"


