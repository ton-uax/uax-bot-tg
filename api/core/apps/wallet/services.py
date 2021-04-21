from decimal import Decimal

from core.apps.wallet import models as wallet_models
from core.apps.account import models as account_models
from core.package.ton.api import TonCli
from tonclient import types

from django.core.cache import cache


def create_wallet(tg_id: int) -> dict:
    account = account_models.TelegramAccount.objects.get(tg_id=tg_id)
    wallets = wallet_models.Wallet.objects.filter(account=account, type_wallet="native")
    cli = TonCli(test=True)

    if account.master_mnemonic == "none":
        mnemonic = cli.create_mnemonic_from_random()
        account.master_mnemonic = mnemonic
        account.save()
    else:
        mnemonic = account.master_mnemonic
        old_wallet = wallets.filter(status="active")[0]
        old_wallet.status = "inactive"
        old_wallet.save()
        update_wallet_cache(old_wallet)

    keypair = cli.get_keypair_from_mnemonic(mnemonic, wallets.count())
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


def add_wallet_from_mnemonic(tg_id, mnemonic):
    if not _check_mnemonic(mnemonic):
        return

    account = account_models.TelegramAccount.objects.get(tg_id=tg_id)
    wallets = wallet_models.Wallet.objects.filter(account=account)

    if account.master_mnemonic == "none":
        account.master_mnemonic = mnemonic
        account.save()
    else:
        old_wallet = wallets.filter(status="active")[0]
        old_wallet.status = "inactive"
        old_wallet.save()
        update_wallet_cache(old_wallet)

    cli = TonCli(test=True)
    n = 0
    for child_index in range(99999):
        try:
            keypair = cli.get_keypair_from_mnemonic(mnemonic, child_index)
            address = cli.get_address(keypair.public)
            if not cli.check_address(address):
                n += 1
                if n > 50:
                    break
                continue
            n = 0
            check_ = wallets.filter(address=address).exists()
            if check_:
                continue

            wallet_title = get_new_title(account)
            balance = cli.get_uax_balance(address)
            new_wallet = wallet_models.Wallet.objects.create(
                account=account,
                address=address,
                title=wallet_title,
                public=keypair.public,
                secret=keypair.secret,
                mnemonic=mnemonic,
                status="inactive",
                balance=int(balance)
            )
            update_wallet_cache(new_wallet)

        except Exception as e:
            print(e)
            break

    active_wallet = wallet_models.Wallet.objects.filter(account=account, mnemonic=mnemonic)[0]
    active_wallet.status = "active"
    active_wallet.save()

    update_wallet_cache(active_wallet)
    return True


def _check_mnemonic(mnemonic):
    cli = TonCli(test=True)
    params = types.ParamsOfMnemonicVerify(phrase=mnemonic)
    return cli.crypto.mnemonic_verify(params=params).valid



def get_new_title(account):
    wallets = wallet_models.Wallet.objects.filter(account=account).exclude(status="deleted")

    if wallets.exists():
        return f"My Wallet #{wallets.count() + 1}"

    return f"My Wallet #1"


def update_wallet_cache(update_wallet):
    wallets_cache = cache.get(f"wallets:{update_wallet.account.tg_id}")

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


def activate_wallet(wallet_id):
    wallet = wallet_models.Wallet.objects.get(id=wallet_id)
    if wallet.status == "active":
        return

    active_wallet = wallet_models.Wallet.objects.filter(account=wallet.account, status="active")[0]
    active_wallet.status = "inactive"
    active_wallet.save()
    update_wallet_cache(active_wallet)
    wallet.status = "active"
    wallet.save()
    update_wallet_cache(wallet)


def edit_wallet_title(wallet_id: int, new_title):
    wallet = wallet_models.Wallet.objects.get(id=wallet_id)
    wallet.title = new_title
    wallet.save()
    update_wallet_cache(wallet)


def delete_wallet(wallet_id: int):
    wallet = wallet_models.Wallet.objects.get(id=wallet_id)
    wallet.status = "deleted"
    wallet.save()
    wallets_cache = cache.get(f"wallets:{wallet.account.tg_id}")
    del(wallets_cache[wallet.id])

    active_wallet = wallet_models.Wallet.objects.filter(account=wallet.account).exclude(status="deleted")[0]
    active_wallet.status = "active"
    active_wallet.save()
    wallets_cache[active_wallet.id]["status"] = "active"
    cache.set(f"wallets:{wallet.account.tg_id}", wallets_cache, timeout=None)