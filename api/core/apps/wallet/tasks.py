from core.config.celery import app as celery_app
from core.apps.wallet import models as wallet_models
from core.package.ton.api import TonCli
from core.package.helpbot.api.pyroAPI import HelpBot
from core.apps.wallet import services as wallet_services
from django.core.cache import cache

@celery_app.task
def check_balance():
    wallets = wallet_models.Wallet.objects.all().exclude(status="deleted")

    cli = TonCli(test=True)
    bot = HelpBot(session_name="refill_session")
    update_wallets = []
    for wallet in wallets:
        new_balance = int(cli.get_uax_balance(wallet.address))

        if new_balance != wallet.balance:
            if new_balance > wallet.balance:

                refill = new_balance - wallet.balance
                wallet.balance = new_balance
                update_wallets.append(wallet)
                bot.send_msg(wallet.account.tg_id, f"Your wallet **{wallet.title}** is replenished with **{refill}** UAX", open_wallet=True, wallet_id=wallet.id)
            elif new_balance < wallet.balance:
                wallet.balance = new_balance
                update_wallets.append(wallet)

            wallet_services.update_wallet_cache(wallet)

    wallet_models.Wallet.objects.bulk_update(update_wallets, fields=["balance"])


@celery_app.task
def check_fee():
    cli = TonCli(test=True)
    fee = cli.get_fee()
    cache.set("fee", {"fee": fee}, timeout=None)