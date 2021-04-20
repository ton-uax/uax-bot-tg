from decimal import Decimal

from pyrogram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from config import cache

def first_start():
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Create wallet", callback_data="new_wallet"),
             InlineKeyboardButton("Add wallet", callback_data="add_wallet")]
        ]
    )

    return kb


def wallet_menu():
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Send", callback_data="menu-send"),
             InlineKeyboardButton("Receive", callback_data="menu-recive")],
            [InlineKeyboardButton("Games", callback_data="menu-games"),
             InlineKeyboardButton("Settings", callback_data="menu-settings")]
        ]
    )
    return kb


def back_wallet():
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("« Back to Wallet", callback_data="back_wallet")]
        ]
    )
    return kb


def max_amount(tg_id):
    wallet = cache.get_active_wallet(tg_id)
    max_amount = Decimal(wallet['balance']) - Decimal(1)
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"Use Max - {max_amount} UAX", callback_data=f"send_max-{max_amount}")],
            [InlineKeyboardButton("« Back to Wallet", callback_data="back_wallet")]
        ]
    )
    return kb


def confirm_tx(tg_id, amount):

    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"Send", callback_data=f"confirm_tx-send-{amount}"),
             InlineKeyboardButton("Cancel", callback_data="confirm_tx-cancel")]
        ]
    )
    return kb


def settings(tg_id):
    wallet = cache.get_active_wallet(tg_id)

    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"Current Wallet: {wallet['title']}", callback_data=f"settings-current_wallet")],
            [InlineKeyboardButton("Manage Wallets", callback_data="settings-manage_wallets")],
            [InlineKeyboardButton("« Back to Wallet", callback_data="back_wallet")]
        ]
    )
    return kb


def gen_wallets_kblist(tg_id, callback_data):
    wallets = cache.get_user_wallets(tg_id)

    row = []
    kb = []

    for i in wallets:
        wallet = wallets[i]
        wallet_btn = InlineKeyboardButton(wallet["title"], callback_data=f"{callback_data}-{wallet['id']}")
        row.append(wallet_btn)

        if len(wallets) == 1:
            kb.append(row)
            row = []

        if len(row) == 2:
            kb.append(row)
            row = []

    if len(row) != 0:
        kb.append(row)
    return kb


def current_wallet(tg_id):
    kb = gen_wallets_kblist(tg_id, "settings-select_wallet")
    kb.append([InlineKeyboardButton("« Back to Settings", callback_data="settings-back_settings")])
    return InlineKeyboardMarkup(kb)


def manage_wallets(tg_id):
    kb = gen_wallets_kblist(tg_id, "settings-manage_wallet")

    kb.insert(0, [InlineKeyboardButton("🔐 Add Wallet", callback_data="settings-add_wallet")])
    kb.append([InlineKeyboardButton("« Back to Settings", callback_data="settings-back_settings")])
    return InlineKeyboardMarkup(kb)