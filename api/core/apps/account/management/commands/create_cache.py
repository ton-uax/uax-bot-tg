from django.core.management.base import BaseCommand
from django.core.cache import cache
from core.apps.account import models as account_models
from core.apps.account import services as account_services
from core.apps.wallet import services as wallet_services
from core.apps.wallet import models as wallet_models

class Command(BaseCommand):

    def handle(self, **options):
        users = account_models.TelegramAccount.objects.all()

        for user in users:
            account_services.cache_user(user)

            wallets = wallet_models.Wallet.objects.filter(account=user).exclude(status="deleted")
            for wallet in wallets:
                wallet_services.update_wallet_cache(wallet)

        print("OK!")
