from decimal import Decimal

from pyrogram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from config import cache
import random as r

def first_start():
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Create wallet", callback_data="new_wallet"),
             InlineKeyboardButton("Add wallet", callback_data="settings-seed_phrase")]
        ]
    )

    return kb


def reply(tg_id):
    kb = ReplyKeyboardMarkup(
        [
            ["💳 My Wallet"],
            ["🆔 My Address"]
        ], resize_keyboard=True
    )
    return kb


def wallet_menu():
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Send", callback_data="menu-send"),
             InlineKeyboardButton("Receive", callback_data="menu-recive")],
            [InlineKeyboardButton("Buy", url="https://kuna.io/"),
             InlineKeyboardButton("Settings", callback_data="menu-settings")],
            [InlineKeyboardButton("💎 Earn", callback_data="qqqqqq")]
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
    fee = cache.get_fee()
    max_amount = Decimal(wallet['balance']) - Decimal(fee)
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
    mode = cache.read_user_cache(tg_id, "chat_mode")
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"Current Wallet: {wallet['title']}", callback_data=f"settings-current_wallet")],
            [InlineKeyboardButton("Manage Wallets", callback_data="settings-manage_wallets")],
            [InlineKeyboardButton(f"Chat mode: {mode}", callback_data=f"settings-chat_mode-{mode}")],
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


def add_wallet(tg_id):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"Create wallet", callback_data=f"settings-create_wallet")],
            [InlineKeyboardButton("🔐 Use Own Seed-phrase", callback_data="settings-seed_phrase")],
            [InlineKeyboardButton("« Back to Wallets list", callback_data="settings-manage_wallets")]
        ]
    )
    return kb


def settings_wallet(tg_id, wallet_id):
    wallets = cache.get_user_wallets(tg_id)
    wallet_lock = ""
    wl_cb = ""
    if len(wallets) == 1:
        wallet_lock = " 🔒"
        wl_cb = "dasw"
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"Show Seed Phrase", callback_data=f"wallet_settings-show_phrase-{wallet_id}")],
            [InlineKeyboardButton("Edit Title", callback_data=f"wallet_settings-edit_title-{wallet_id}"),
             InlineKeyboardButton(f"{wallet_lock} Delete Wallet", callback_data=f"wallet_settings-delete_wallet{wl_cb}-{wallet_id}")],
            [InlineKeyboardButton("« Back to Wallets list", callback_data="settings-manage_wallets")]
        ]
    )
    return kb


def delete_wallet_1(tg_id, wallet_id):
    kb_list = [[InlineKeyboardButton("Yes, delete the wallet", callback_data=f"delete_wallet-first-{wallet_id}")],
          [InlineKeyboardButton("No", callback_data=f"wallet_settings-back_wallet-{wallet_id}")],
          [InlineKeyboardButton("Nope, nevermind", callback_data=f"wallet_settings-back_wallet-{wallet_id}")]]
    kb = []
    for i in range(3):
        r.shuffle(kb_list)
        bt = kb_list.pop()
        kb.append(bt)

    kb.append([InlineKeyboardButton("« Back to Wallet", callback_data=f"wallet_settings-back_wallet-{wallet_id}")])
    return InlineKeyboardMarkup(kb)


def delete_wallet_2(tg_id, wallet_id):
    kb_list = [[InlineKeyboardButton("Yes, I'm 100% shure!", callback_data=f"delete_wallet-delete-{wallet_id}")],
          [InlineKeyboardButton("Hell no!", callback_data=f"wallet_settings-back_wallet-{wallet_id}")],
          [InlineKeyboardButton("No!", callback_data=f"wallet_settings-back_wallet-{wallet_id}")]]
    kb = []
    for i in range(3):
        r.shuffle(kb_list)
        bt = kb_list.pop()
        kb.append(bt)

    kb.append([InlineKeyboardButton("« Back to Wallet", callback_data=f"wallet_settings-back_wallet-{wallet_id}")])
    return InlineKeyboardMarkup(kb)


def back_wallet_settings(tg_id, wallet_id):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("« Back to Wallet", callback_data=f"wallet_settings-back_wallet-{wallet_id}")]
        ]
    )
    return kb

def back_add_menu(tg_id):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("« Back", callback_data=f"settings-add_wallet")]
        ]
    )
    return kb


def back_add_wallet(tg_id):
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("« Back", callback_data=f"back_add_wallet")]
        ]
    )
    return kb