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