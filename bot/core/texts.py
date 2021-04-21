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


def settings_wallet(tg_id, wallet_id):
    wallet = cache.get_wallet(tg_id, wallet_id)
    txt = f"Here it is: {wallet['title']}\n\n" \
          f"What do you want to do with the wallet?"
    return txt


def show_phrase(tg_id, wallet_id):
    wallet = cache.get_wallet(tg_id, wallet_id)
    txt = f"Seed phrase for this wallet {wallet['title']}\n\n" \
          f"```{wallet['mnemonic']}```"
    return txt


def edit_title(tg_id):
    txt = "OK. Send me the new title for your wallet."
    return txt


def delete_wallet(tg_id, wallet_id):
    wallet = cache.get_wallet(tg_id, wallet_id)
    txt = f"You are about to delete your wallet {wallet['title']}. Is that correct? "
    return txt


def confirm_delete_wallet(tg_id, wallet_id):
    wallet = cache.get_wallet(tg_id, wallet_id)
    txt = f"You are about to delete your wallet {wallet['title']}. Is that correct?\n\n" \
          f"⚠️ This action cannot be undone. You will lose your money if you didn't save the seed phrase or private key."
    return txt

def deleted_wallet(tg_id, wallet_id):
    wallet = cache.get_wallet(tg_id, wallet_id)
    txt = f"wallet {wallet['title']} has been deleted."
    return txt

def enter_mnemonic(tg_id):
    txt = "Send me a seed phrase or private key:"
    return txt