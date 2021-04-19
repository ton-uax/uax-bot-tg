from pyrogram import Client, Filters, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from core.api import WalletAPI
from core import keyboard as kb
from core import texts
from config import cache


def delete_inline_kb(cli: Client, tg_id: int, msg_id: int):
    try:
        msg = cli.get_messages(tg_id, msg_id)
        msg.edit(msg.text)
    except:
        pass


@Client.on_message(Filters.command('start'))
def start(cli, m):
    tg_id = m.from_user.id

    # Делает проверку зарегестрирован ли юзер
    response = WalletAPI.check_user(tg_id)

    if response.status_code == 200:
        m.reply(texts.wallet_menu(tg_id), reply_markup=kb.wallet_menu())
    if response.status_code == 404:
        WalletAPI.registration_user(m.from_user)
        m.reply('Do you want to create a wallet or add an existing one', reply_markup=kb.first_start())


@Client.on_callback_query(Filters.callback_data("new_wallet"))
def new_wallet(cli, cb):
    tg_id = cb.from_user.id
    cb.message.edit(cb.message.text)
    wallet = WalletAPI.create_wallet(tg_id)

    cb.message.reply(texts.wallet_menu(tg_id), reply_markup=kb.wallet_menu())


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith("menu")))
def wallet_menu(cli, cb):
    tg_id = cb.from_user.id
    btn = cb.data.split("-")[1]
    wallet = cache.get_active_wallet(tg_id)
    if btn == "send":

        if wallet["balance"] > 1:
            cache.change_user_flag(tg_id, "await_to_address", True)
            msg = cb.message.edit("Send me an address to send UAX:", reply_markup=kb.back_wallet())
            cache.write_user_cache(tg_id, "last_msg_id", msg.message_id)
        else:
            cb.message.edit("Insufficient funds", reply_markup=kb.back_wallet())
    elif btn == "recive":
        cb.message.edit(wallet["address"], reply_markup=kb.back_wallet())
    elif btn == "settings":
        pass


@Client.on_callback_query(Filters.callback_data("back_wallet"))
def back_wallet(cli, cb):
    tg_id = cb.from_user.id
    cache.change_user_flag(tg_id, "await_to_address", False)
    cache.change_user_flag(tg_id, "await_to_amount", False)
    cb.message.edit(texts.wallet_menu(tg_id), reply_markup=kb.wallet_menu())


@Client.on_message(~Filters.bot & Filters.create(lambda _, m: cache.get_user_flags(m.from_user.id)["await_to_address"]))
def await_address_to(cli, m):
    tg_id = m.from_user.id
    valid_address = WalletAPI.check_wallet(m.text)

    delete_inline_kb(cli, tg_id, cache.read_user_cache(tg_id, "last_msg_id"))
    if valid_address:
        cache.change_user_flag(tg_id, "await_to_address", False)
        cache.change_user_flag(tg_id, "await_to_amount", True)
        cache.write_user_cache(tg_id, "address_to", m.text)
        msg = m.reply("Send me an amount in UAX", reply_markup=kb.max_amount(tg_id))
    else:
        msg = m.reply("invalid address", reply_markup=kb.back_wallet())

    cache.write_user_cache(tg_id, "last_msg_id", msg.message_id)


@Client.on_message(~Filters.bot & Filters.create(lambda _, m: cache.get_user_flags(m.from_user.id)["await_to_amount"]))
def await_amount_to(cli, m):
    tg_id = m.from_user.id
    wallet = cache.get_active_wallet(tg_id)
    delete_inline_kb(cli, tg_id, cache.read_user_cache(tg_id, "last_msg_id"))
    try:
        amount = int(m.text)
        if amount + 1 > wallet["balance"]:
            raise Exception
    except:
        m.reply("Invalid amount")
        return
    cache.change_user_flag(tg_id, "await_to_amount", False)
    m.reply(texts.confirm_transaction(cache.read_user_cache(tg_id, "address_to"), amount), reply_markup=kb.confirm_tx(tg_id, amount))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith("send_max")))
def send_max(cli, cb):
    tg_id = cb.from_user.id
    wallet = cache.get_active_wallet(tg_id)
    amount = wallet["balance"] - 1
    cache.change_user_flag(tg_id, "await_to_amount", False)
    cb.message.edit(texts.confirm_transaction(cache.read_user_cache(tg_id, "address_to"), amount), reply_markup=kb.confirm_tx(tg_id, amount))


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith("confirm_tx")))
def confirm_tx(cli, cb):
    tg_id = cb.from_user.id
    action = cb.data.split('-')[1]
    address_to = cache.read_user_cache(tg_id, "address_to")
    if action == "send":
        amount = cb.data.split('-')[2]
        WalletAPI.send_tx(tg_id, address_to, amount)
        cb.message.edit(texts.success_tx(amount, address_to))
        cb.message.reply(texts.wallet_menu(tg_id), reply_markup=kb.wallet_menu())
    elif action == "cancel":
        back_wallet(cli, cb)