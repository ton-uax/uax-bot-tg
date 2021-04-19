from django.contrib import admin

from core.apps.wallet import models as wallet_models


@admin.register(wallet_models.Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("account", "address", "public", "status")

