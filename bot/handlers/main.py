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
        delete_inline_kb(cli, tg_id, cache.read_user_cache(tg_id, "wallet_menu_id"))
        msg = m.reply(texts.wallet_menu(tg_id), reply_markup=kb.wallet_menu())
        cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)
    if response.status_code == 404:
        WalletAPI.registration_user(m.from_user)
        m.reply('Do you want to create a wallet or add an existing one', reply_markup=kb.first_start())


@Client.on_callback_query(Filters.callback_data("new_wallet"))
def new_wallet(cli, cb):
    tg_id = cb.from_user.id
    cb.message.edit(cb.message.text)
    wallet = WalletAPI.create_wallet(tg_id)
    msg = cb.message.reply(texts.wallet_menu(tg_id), reply_markup=kb.wallet_menu())
    cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith("menu")))
def wallet_menu(cli, cb):
    tg_id = cb.from_user.id
    btn = cb.data.split("-")[1]
    wallet = cache.get_active_wallet(tg_id)
    if btn == "send":

        if wallet["balance"] > 1:
            cache.change_user_flag(tg_id, "await_to_address", True)
            cb.message.edit(cb.message.text)
            msg = cb.message.reply("Send me an address to send UAX:", reply_markup=kb.back_wallet())
            cache.write_user_cache(tg_id, "last_msg_id", msg.message_id)
        else:
            cb.message.edit(cb.message.text)
            cb.message.edit("Insufficient funds", reply_markup=kb.back_wallet())
            cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)
    elif btn == "recive":
        cb.message.edit(cb.message.text)
        msg = cb.message.reply(wallet["address"], reply_markup=kb.back_wallet())
        cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)
    elif btn == "settings":
        cb.message.edit(cb.message.text)
        msg = cb.message.reply(texts.wallet_settings(tg_id), reply_markup=kb.settings(tg_id))
        cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)


@Client.on_callback_query(Filters.callback_data("back_wallet"))
def back_wallet(cli, cb):
    tg_id = cb.from_user.id
    cache.change_user_flag(tg_id, "await_to_address", False)
    cache.change_user_flag(tg_id, "await_to_amount", False)
    cb.message.edit(cb.message.text)
    msg = cb.message.reply(texts.wallet_menu(tg_id), reply_markup=kb.wallet_menu())
    cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)


@Client.on_message(~Filters.bot & Filters.create(lambda _, m: cache.get_user_flags(m.from_user.id)["await_to_address"]))
def await_address_to(cli, m):
    tg_id = m.from_user.id
    valid_address = WalletAPI.check_wallet(m.text)

    delete_inline_kb(cli, tg_id, cache.read_user_cache(tg_id, "last_msg_id"))
    if valid_address:
        cache.change_user_flag(tg_id, "await_to_address", False)
        cache.change_user_flag(tg_id, "await_to_amount", True)
        cache.write_user_cache(tg_id, "address_to", m.text)
        msg = m.reply("Enter amount in UAX", reply_markup=kb.max_amount(tg_id))
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
    cb.message.edit(cb.message.text)
    msg = cb.message.reply(texts.confirm_transaction(cache.read_user_cache(tg_id, "address_to"), amount), reply_markup=kb.confirm_tx(tg_id, amount))
    cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith("confirm_tx")))
def confirm_tx(cli, cb):
    tg_id = cb.from_user.id
    action = cb.data.split('-')[1]
    address_to = cache.read_user_cache(tg_id, "address_to")
    if action == "send":
        amount = int(cb.data.split('-')[2])
        WalletAPI.send_tx(tg_id, address_to, amount)
        cb.message.edit(texts.success_tx(amount, address_to))
        delete_inline_kb(cli, tg_id, cache.read_user_cache(tg_id, "wallet_menu_id"))
        msg = cb.message.reply(texts.wallet_menu(tg_id), reply_markup=kb.wallet_menu())
        cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)
    elif action == "cancel":
        back_wallet(cli, cb)


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith("settings")))
def settings(cli, cb):
    tg_id = cb.from_user.id
    action = cb.data.split('-')[1]

    if action == "current_wallet":
        cb.message.edit(cb.message.text)
        msg = cb.message.reply(texts.current_wallet(tg_id), reply_markup=kb.current_wallet(tg_id))
        cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)

    elif action == "manage_wallets":
        cb.message.edit(cb.message.text)
        msg = cb.message.reply(texts.manage_wallets(tg_id), reply_markup=kb.manage_wallets(tg_id))
        cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)

    elif action == "select_wallet":
        wallet_id = cb.data.split('-')[2]
        WalletAPI.activate_wallet(wallet_id)
        delete_inline_kb(cli, tg_id, cache.read_user_cache(tg_id, "wallet_menu_id"))
        delete_inline_kb(cli, tg_id, cb.message.message_id)
        msg = cb.message.reply(texts.wallet_menu(tg_id), reply_markup=kb.wallet_menu())
        cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)

    elif action == "add_wallet":
        cache.change_user_flag(tg_id, "await_mnemonic", False)
        cb.message.edit(cb.message.text)
        msg = cb.message.reply(texts.add_wallet(tg_id), reply_markup=kb.add_wallet(tg_id))
        cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)

    elif action == "create_wallet":
        new_wallet(cli, cb)
    elif action == "seed_phrase":
        cache.change_user_flag(tg_id, "await_mnemonic", True)
        cb.message.edit(cb.message.text)
        msg = cb.message.reply(texts.enter_mnemonic(tg_id))
        cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)

    elif action == "manage_wallet":
        wallet_id = int(cb.data.split("-")[2])
        cb.message.edit(cb.message.text)
        msg = cb.message.reply(texts.settings_wallet(tg_id, wallet_id), reply_markup=kb.settings_wallet(tg_id, wallet_id))
        cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)

    elif action == "back_settings":
        cb.message.edit(cb.message.text)
        msg = cb.message.reply(texts.wallet_settings(tg_id), reply_markup=kb.settings(tg_id))
        cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith("wallet_settings")))
def wallet_settings(cli, cb):
    tg_id = cb.from_user.id
    action = cb.data.split('-')[1]
    wallet_id = int(cb.data.split("-")[2])
    if action == "show_phrase":
        cb.message.edit(cb.message.text)
        msg = cb.message.reply(texts.show_phrase(tg_id, wallet_id), reply_markup=kb.back_wallet_settings(tg_id, wallet_id))
        cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)

    elif action == "edit_title":
        cache.change_user_flag(tg_id, "await_wallet_title", True)
        cache.write_user_cache(tg_id, "last_wallet_id", wallet_id)
        cb.message.edit(cb.message.text)
        msg = cb.message.reply(texts.edit_title(tg_id), reply_markup=kb.back_wallet_settings(tg_id, wallet_id))
        cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)

    elif action == "delete_wallet":
        cb.message.edit(cb.message.text)
        msg = cb.message.reply(texts.delete_wallet(tg_id, wallet_id), reply_markup=kb.delete_wallet_1(tg_id, wallet_id))
        cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)

    elif action == "back_wallet":
        cache.change_user_flag(tg_id, "await_wallet_title", False)
        cb.message.edit(cb.message.text)
        msg = cb.message.reply(texts.settings_wallet(tg_id, wallet_id), reply_markup=kb.settings_wallet(tg_id, wallet_id))
        cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith("delete_wallet")))
def delete_wallet(cli, cb):
    tg_id = cb.from_user.id
    action = cb.data.split('-')[1]
    wallet_id = int(cb.data.split("-")[2])

    if action == "first":
        cb.message.edit(cb.message.text)
        msg = cb.message.reply(texts.confirm_delete_wallet(tg_id, wallet_id), reply_markup=kb.delete_wallet_2(tg_id, wallet_id))
        cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)
    if action == "delete":
        cb.message.edit(cb.message.text)
        cb.message.reply(texts.deleted_wallet(tg_id, wallet_id))
        WalletAPI.delete_wallet(wallet_id)
        msg = cb.message.reply(texts.manage_wallets(tg_id), reply_markup=kb.manage_wallets(tg_id))
        cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)


@Client.on_message(~Filters.bot & Filters.create(lambda _, m: cache.get_user_flags(m.from_user.id)["await_wallet_title"]))
def wallet_title(cli, m):
    tg_id = m.from_user.id
    title = m.text
    cache.change_user_flag(tg_id, "await_wallet_title", False)
    wallet_id = cache.read_user_cache(tg_id, "last_wallet_id")
    WalletAPI.edit_title(wallet_id, title)
    delete_inline_kb(cli, tg_id, cache.read_user_cache(tg_id, "wallet_menu_id"))

    msg = m.reply(texts.settings_wallet(tg_id, wallet_id), reply_markup=kb.settings_wallet(tg_id, wallet_id))
    cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)


@Client.on_message(~Filters.bot & Filters.create(lambda _, m: cache.get_user_flags(m.from_user.id)["await_mnemonic"]))
def await_mnemonic(cli, m):
    tg_id = m.from_user.id
    mnemonic = m.text
    if not WalletAPI.add_from_mnemonic(tg_id, mnemonic):
        return m.reply("Bad phrase", reply_markup=kb.back_add_menu(tg_id))

    cache.change_user_flag(tg_id, "await_mnemonic", False)
    delete_inline_kb(cli, tg_id, cache.read_user_cache(tg_id, "wallet_menu_id"))
    msg = m.reply(texts.wallet_menu(tg_id), reply_markup=kb.wallet_menu())
    cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith("back_settings")))
def back_settings(cli, cb):
    tg_id = cb.from_user.id
    cb.message.edit(cb.message.text)
    msg = cb.message.reply(texts.wallet_settings(tg_id), reply_markup=kb.settings(tg_id))
    cache.write_user_cache(tg_id, "wallet_menu_id", msg.message_id)