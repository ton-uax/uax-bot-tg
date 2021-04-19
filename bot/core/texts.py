from config import cache


def wallet_menu(tg_id):
    wallets = cache.get_user_wallets(tg_id)
    for i in wallets:
        if wallets[i]["status"] == "active":
            wallet = wallets[i]

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