from decimal import Decimal

from core.apps.wallet import models as wallet_models
from core.apps.account import models as account_models
from core.package.ton.api import TonCli
from tonclient import types

from django.core.cache import cache


def create_wallet(tg_id: int) -> dict:
    account = account_models.TelegramAccount.objects.get(tg_id=tg_id)

    cli = TonCli(test=True)

    if account.master_mnemonic == "none":
        mnemonic = cli.create_mnemonic_from_random()
        account.master_mnemonic = mnemonic
        account.save()
    else:
        mnemonic = account.master_mnemonic
        old_wallet = wallet_models.Wallet.objects.filter(tg_id=tg_id, status="active")
        old_wallet.status = "inactive"
        old_wallet.save()

    keypair = cli.mnemonic_derive_sign_keys(mnemonic)
    address = cli.deploy_with_key(keypair.public)
    wallet_title = get_new_title(account)

    new_wallet = wallet_models.Wallet.objects.create(
        account=account,
        address=address,
        title=wallet_title,
        public=keypair.public,
        secret=keypair.secret,
        mnemonic=mnemonic
    )

    return update_wallet_cache(new_wallet)


def get_new_title(account):
    wallets = wallet_models.Wallet.objects.filter(account=account).exclude(status="deleted")

    if wallets.exists():
        return f"My Wallet #{wallets.count()+1}"

    return f"My Wallet #1"


def update_wallet_cache(update_wallet):
    wallets_cache = cache.get(f"wallets:{update_wallet.account.tg_id}")

    old_wallet = wallets_cache.get(update_wallet.id, None)

    if old_wallet:
        wallets_cache[update_wallet.id]["balance"] = update_wallet.balance
        wallets_cache[update_wallet.id]["title"] = update_wallet.title
    else:
        wallets_cache[update_wallet.id] = {
            "id": update_wallet.id,
            "address": update_wallet.address,
            "title": update_wallet.title,
            "mnemonic": update_wallet.mnemonic,
            "status": update_wallet.status,
            "type_wallet": update_wallet.type_wallet,
            "balance": update_wallet.balance
        }

    cache.set(f"wallets:{update_wallet.account.tg_id}", wallets_cache, timeout=None)
    return wallets_cache[update_wallet.id]


def send_tx(data):
    tg_id = data["sender_id"]
    address_to = data["address_to"]
    amount = int(data["amount"])

    account = account_models.TelegramAccount.objects.get(tg_id=tg_id)
    wallet = wallet_models.Wallet.objects.filter(account=account, status="active")[0]

    cli = TonCli(test=True)
    keypair = types.KeyPair(public=wallet.public, secret=wallet.secret)
    cli.send_tx(wallet.address, keypair, address_to, amount)
    wallet.balance = wallet.balance - amount - 1

    update_wallet_cache(wallet)