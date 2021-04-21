from config import cache


def wallet_menu(tg_id):
    wallet = cache.get_active_wallet(tg_id)

    wallet_txt = f"Balance of {wallet['title']}:\n\n" \
                 f"~ {wallet['balance']} UAX"

    return wallet_txt


def confirm_transaction(address, amount):
    txt = f"⚡️ **Confirm transaction**\n\n" \
          f"👤\n" \
          f"{address}\n\n" \
          f"🎗 **{amount}** UAX\n\n" \
          f"Transaction fee: **1** UAX"
    return txt


def success_tx(amount, address_to):
    txt = f"**{amount}** UAX sent to\n\n" \
          f"{address_to}"
    return txt


def wallet_settings(tg_id):
    txt = "Here you can change the current wallet and manage your wallets"
    return txt


def current_wallet(tg_id):
    txt = "Choose a wallet you want to open:"
    return txt


def manage_wallets(tg_id):
    txt = "Here you can create a new wallet or manage your wallets."
    return txt


def add_wallet(tg_id):
    txt = "Do you want to create a new wallet or add a wallet by seed phrase?\n\n" \
          "⚠️ We store your private keys in an encrypted form signed with a unique key. " \
          "But we strongly recommend that you keep your seed phrase securely."
    return txt