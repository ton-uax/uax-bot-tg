from pyrogram import Client, Filters, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from core.api import WalletAPI


@Client.on_message(Filters.command('start'))
def start(cli, m):
    tg_id = m.from_user.id

    # Делает проверку зарегестрирован ли юзер
    response = WalletAPI.check_user(tg_id)

    if response.status_code == 200:
       pass
    if response.status_code == 404:
        m.reply('Hi')
