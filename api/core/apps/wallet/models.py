from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _

from core.apps.common import models as common_models


class Wallet(common_models.BaseModel):
    account = models.ForeignKey("account.TelegramAccount", verbose_name=_("Телеграм аккаунт"), related_name="wallets", on_delete=models.CASCADE)
    title = models.CharField(_("Имя кошелька"), max_length=255)
    address = models.CharField(_("Адрес кошелька"), max_length=255)
    public = models.CharField(_("Публичный ключ"), max_length=255)
    secret = models.CharField(_("Секретный ключ"), max_length=255)
    mnemonic = models.CharField(_("Мнемоническая фраза"), max_length=255, default=' ')
    balance = models.PositiveIntegerField(_("Баланс"), default=0)
    status = models.CharField(
        _("Статус"),
        max_length=50,
        choices=(
            ("active", _("Активный")),
            ("inactive", _("Неактивный")),
            ("deleted", _("Удалён"))

        ), default="active")

    type_wallet = models.CharField(
        _("Тип кошелька"),
        max_length=50,
        choices=(
            ("native", _("Внутренний")),
            ("vendor", _("Сторонний"))
        ), default="native")

    class Meta:
        verbose_name = 'Кошелёк'
        verbose_name_plural = 'Кошельки'

    def __str__(self):
        return f"{self.account} {self.title}"


