from pyrogram import Client, Filters, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from core.api import WalletAPI
from core import keyboard as kb
from core import texts
from config import cache


def new_msg(cli, m, tg_id, text, kb, cache_read, cache_write, type):
    user_set = cache.read_user_cache(tg_id, "chat_mode")

    if user_set == "Historical":
        if type == "on_message":
            delete_inline_kb(cli, tg_id, cache.read_user_cache(tg_id, cache_read))
            msg = cli.send_message(tg_id, text, reply_markup=kb)
            cache.write_user_cache(tg_id, cache_write, msg.message_id)
        if type == "on_callback":
            m.message.edit(m.message.text)
            msg = m.message.reply(text, reply_markup=kb)
            cache.write_user_cache(tg_id, cache_write, msg.message_id)

    if user_set == "Modern":
        if type == "on_message":
            delete_inline_kb(cli, tg_id, cache.read_user_cache(tg_id, cache_read))
            msg = cli.send_message(tg_id, text, reply_markup=kb)
            cache.write_user_cache(tg_id, cache_write, msg.message_id)
        if type == "on_callback":
            msg = m.message.edit(text, reply_markup=kb)
            cache.write_user_cache(tg_id, cache_write, msg.message_id)


def delete_inline_kb(cli: Client, tg_id: int, msg_id: int):
    try:
        msg = cli.get_messages(tg_id, msg_id)
        msg.edit(msg.text)
    except:
        pass


@Client.on_message(Filters.regex(r"^💳 My Wallet"))
def my_w(cli, m):
    tg_id = m.from_user.id
    new_msg(cli, m, tg_id, texts.wallet_menu(tg_id), kb.wallet_menu(), "wallet_menu_id", "wallet_menu_id", "on_message")


@Client.on_message(Filters.regex(r"^🆔 My Address"))
def my_adr(cli, m):
    wallet = cache.get_active_wallet(m.from_user.id)
    m.reply(wallet["address"])


@Client.on_message(Filters.command('start'))
def start(cli, m):
    tg_id = m.from_user.id

    # Делает проверку зарегестрирован ли юзер
    response = WalletAPI.check_user(tg_id)

    if response.status_code == 200:
        new_msg(cli, m, tg_id, texts.wallet_menu(tg_id), kb.wallet_menu(), "wallet_menu_id", "wallet_menu_id",
                "on_message")
    if response.status_code == 404:
        WalletAPI.registration_user(m.from_user)
        m.reply('Do you want to create a wallet or add an existing one', reply_markup=kb.first_start())


@Client.on_callback_query(Filters.callback_data("new_wallet"))
def new_wallet(cli, cb):
    tg_id = cb.from_user.id
    check_ = cache.get_user_wallets(tg_id)
    cb.message.edit(cb.message.text)
    cli.answer_callback_query(cb.id, "Wait a moment. I'm creating a wallet for you.", show_alert=True)
    wallet = WalletAPI.create_wallet(tg_id)
    if len(check_) == 0:
        cb.message.reply("Welcome to UAX Wallet", reply_markup=kb.reply(tg_id))
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

            new_msg(cli, cb, tg_id, "Send me an address to send UAX:", kb.back_wallet(), "wallet_menu_id", "wallet_menu_id",
                    "on_callback")
        else:
            new_msg(cli, cb, tg_id, "Insufficient funds", kb.back_wallet(), "wallet_menu_id",
                    "wallet_menu_id",
                    "on_callback")

    elif btn == "recive":
        new_msg(cli, cb, tg_id,
                wallet["address"],
                kb.back_wallet(),
                "wallet_menu_id",
                "wallet_menu_id",
                "on_callback")

    elif btn == "settings":
        new_msg(cli, cb, tg_id,
                texts.wallet_settings(tg_id),
                kb.settings(tg_id),
                "wallet_menu_id",
                "wallet_menu_id",
                "on_callback")


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith("open_wallet")))
def open_repl_wallet(cli, cb):
    tg_id = cb.from_user.id
    wallet_id = cb.data.split('-')[1]
    WalletAPI.activate_wallet(wallet_id)
    cb.message.edit(cb.message.text)
    # delete_inline_kb(cli, tg_id, cb.message.message_id)
    new_msg(cli, cb, tg_id,
            texts.wallet_menu(tg_id),
            kb.wallet_menu(),
            "wallet_menu_id",
            "wallet_menu_id",
            "on_message")


@Client.on_callback_query(Filters.callback_data("back_wallet"))
def back_wallet(cli, cb):
    tg_id = cb.from_user.id
    cache.change_user_flag(tg_id, "await_to_address", False)
    cache.change_user_flag(tg_id, "await_to_amount", False)
    cache.change_user_flag(tg_id, "await_wallet_title", False)

    new_msg(cli, cb, tg_id,
            texts.wallet_menu(tg_id),
            kb.wallet_menu(),
            "wallet_menu_id",
            "wallet_menu_id",
            "on_callback")


@Client.on_message(~Filters.bot & Filters.create(lambda _, m: cache.get_user_flags(m.from_user.id)["await_to_address"]))
def await_address_to(cli, m):
    tg_id = m.from_user.id
    valid_address = WalletAPI.check_wallet(m.text)

    delete_inline_kb(cli, tg_id, cache.read_user_cache(tg_id, "last_msg_id"))
    if valid_address:
        cache.change_user_flag(tg_id, "await_to_address", False)
        cache.change_user_flag(tg_id, "await_to_amount", True)
        cache.write_user_cache(tg_id, "address_to", m.text)
        txt = "Enter amount in UAX"
        kbq = kb.max_amount(tg_id)
    else:
        txt = "invalid address"
        kbq = kb.back_wallet()

    new_msg(cli, m, tg_id,
            txt,
            kbq,
            "wallet_menu_id",
            "wallet_menu_id",
            "on_message")


@Client.on_message(~Filters.bot & Filters.create(lambda _, m: cache.get_user_flags(m.from_user.id)["await_to_amount"]))
def await_amount_to(cli, m):
    tg_id = m.from_user.id
    wallet = cache.get_active_wallet(tg_id)
    delete_inline_kb(cli, tg_id, cache.read_user_cache(tg_id, "last_msg_id"))
    fee = cache.get_fee()
    try:
        amount = int(m.text)
        if amount + fee > wallet["balance"]:
            raise Exception
    except:
        m.reply("Invalid amount")
        new_msg(cli, m, tg_id,
                "Invalid amount",
                kb.back_wallet(tg_id),
                "wallet_menu_id",
                "wallet_menu_id",
                "on_message")
        return
    cache.change_user_flag(tg_id, "await_to_amount", False)

    new_msg(cli, m, tg_id,
            texts.confirm_transaction(cache.read_user_cache(tg_id, "address_to"), amount),
            kb.confirm_tx(tg_id, amount),
            "wallet_menu_id",
            "wallet_menu_id",
            "on_message")


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith("send_max")))
def send_max(cli, cb):
    tg_id = cb.from_user.id
    wallet = cache.get_active_wallet(tg_id)
    fee = cache.get_fee()
    amount = wallet["balance"] - fee
    cache.change_user_flag(tg_id, "await_to_amount", False)
    new_msg(cli, cb, tg_id,
            texts.confirm_transaction(cache.read_user_cache(tg_id, "address_to"), amount),
            kb.confirm_tx(tg_id, amount),
            "wallet_menu_id",
            "wallet_menu_id",
            "on_callback")


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
        new_msg(cli, cb, tg_id,
                texts.current_wallet(tg_id),
                kb.current_wallet(tg_id),
                "wallet_menu_id",
                "wallet_menu_id",
                "on_callback")

    elif action == "manage_wallets":
        new_msg(cli, cb, tg_id,
                texts.manage_wallets(tg_id),
                kb.manage_wallets(tg_id),
                "wallet_menu_id",
                "wallet_menu_id",
                "on_callback")

    elif action == "select_wallet":
        wallet_id = cb.data.split('-')[2]
        WalletAPI.activate_wallet(wallet_id)
        #delete_inline_kb(cli, tg_id, cb.message.message_id)
        new_msg(cli, cb, tg_id,
                texts.wallet_menu(tg_id),
                kb.wallet_menu(),
                "wallet_menu_id",
                "wallet_menu_id",
                "on_callback")

    elif action == "add_wallet":
        cache.change_user_flag(tg_id, "await_mnemonic", False)
        new_msg(cli, cb, tg_id,
                texts.add_wallet(tg_id),
                kb.add_wallet(tg_id),
                "wallet_menu_id",
                "wallet_menu_id",
                "on_callback")

    elif action == "create_wallet":
        new_wallet(cli, cb)
    elif action == "seed_phrase":
        cache.change_user_flag(tg_id, "await_mnemonic", True)

        new_msg(cli, cb, tg_id,
                texts.enter_mnemonic(tg_id),
                kb.back_add_wallet(tg_id),
                "wallet_menu_id",
                "wallet_menu_id",
                "on_callback")

    elif action == "manage_wallet":
        wallet_id = int(cb.data.split("-")[2])
        new_msg(cli, cb, tg_id,
                texts.settings_wallet(tg_id, wallet_id),
                kb.settings_wallet(tg_id, wallet_id),
                "wallet_menu_id",
                "wallet_menu_id",
                "on_callback")
    elif action == "chat_mode":
        current_mode = cb.data.split("-")[2]
        if current_mode == "Historical":
            cache.write_user_cache(tg_id, "chat_mode", "Modern")
        else:
            cache.write_user_cache(tg_id, "chat_mode", "Historical")

        new_msg(cli, cb, tg_id,
                texts.wallet_settings(tg_id),
                kb.settings(tg_id),
                "wallet_menu_id",
                "wallet_menu_id",
                "on_callback")

    elif action == "back_settings":
        new_msg(cli, cb, tg_id,
                texts.wallet_settings(tg_id),
                kb.settings(tg_id),
                "wallet_menu_id",
                "wallet_menu_id",
                "on_callback")


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith("wallet_settings")))
def wallet_settings(cli, cb):
    tg_id = cb.from_user.id
    action = cb.data.split('-')[1]
    wallet_id = int(cb.data.split("-")[2])
    if action == "show_phrase":
        new_msg(cli, cb, tg_id,
                texts.show_phrase(tg_id, wallet_id),
                kb.back_wallet_settings(tg_id, wallet_id),
                "wallet_menu_id",
                "wallet_menu_id",
                "on_callback")

    elif action == "edit_title":
        cache.change_user_flag(tg_id, "await_wallet_title", True)
        cache.write_user_cache(tg_id, "last_wallet_id", wallet_id)
        new_msg(cli, cb, tg_id,
                texts.edit_title(tg_id),
                kb.back_wallet_settings(tg_id, wallet_id),
                "wallet_menu_id",
                "wallet_menu_id",
                "on_callback")

    elif action == "delete_wallet":

        new_msg(cli, cb, tg_id,
                texts.delete_wallet(tg_id, wallet_id),
                kb.delete_wallet_1(tg_id, wallet_id),
                "wallet_menu_id",
                "wallet_menu_id",
                "on_callback")

    elif action == "back_wallet":
        cache.change_user_flag(tg_id, "await_wallet_title", False)
        new_msg(cli, cb, tg_id,
                texts.settings_wallet(tg_id, wallet_id),
                kb.settings_wallet(tg_id, wallet_id),
                "wallet_menu_id",
                "wallet_menu_id",
                "on_callback")


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith("delete_wallet")))
def delete_wallet(cli, cb):
    tg_id = cb.from_user.id
    action = cb.data.split('-')[1]
    wallet_id = int(cb.data.split("-")[2])

    if action == "first":
        new_msg(cli, cb, tg_id,
                texts.confirm_delete_wallet(tg_id, wallet_id),
                kb.delete_wallet_2(tg_id, wallet_id),
                "wallet_menu_id",
                "wallet_menu_id",
                "on_callback")

    if action == "delete":
        cb.message.reply(texts.deleted_wallet(tg_id, wallet_id))
        WalletAPI.delete_wallet(wallet_id)
        new_msg(cli, cb, tg_id,
                texts.manage_wallets(tg_id),
                kb.manage_wallets(tg_id),
                "wallet_menu_id",
                "wallet_menu_id",
                "on_callback")


@Client.on_message(~Filters.bot & Filters.create(lambda _, m: cache.get_user_flags(m.from_user.id)["await_wallet_title"]))
def wallet_title(cli, m):
    tg_id = m.from_user.id
    title = m.text
    cache.change_user_flag(tg_id, "await_wallet_title", False)
    wallet_id = cache.read_user_cache(tg_id, "last_wallet_id")
    WalletAPI.edit_title(wallet_id, title)

    new_msg(cli, m, tg_id,
            texts.settings_wallet(tg_id, wallet_id),
            kb.settings_wallet(tg_id, wallet_id),
            "wallet_menu_id",
            "wallet_menu_id",
            "on_message")


@Client.on_message(~Filters.bot & Filters.create(lambda _, m: cache.get_user_flags(m.from_user.id)["await_mnemonic"]))
def await_mnemonic(cli, m):
    tg_id = m.from_user.id
    check_ = cache.get_user_wallets(tg_id)

    mnemonic = m.text
    if not WalletAPI.add_from_mnemonic(tg_id, mnemonic):
        return new_msg(cli, m, tg_id,
                "Bad phrase",
                kb.back_add_menu(tg_id),
                "wallet_menu_id",
                "wallet_menu_id",
                "on_message")


    if len(check_) == 0:
        m.reply("Welcome to UAX Wallet", reply_markup=kb.reply(tg_id))

    cache.change_user_flag(tg_id, "await_mnemonic", False)
    new_msg(cli, m, tg_id,
            texts.wallet_menu(tg_id),
            kb.wallet_menu(),
            "wallet_menu_id",
            "wallet_menu_id",
            "on_message")


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith("back_settings")))
def back_settings(cli, cb):
    tg_id = cb.from_user.id

    new_msg(cli, cb, tg_id,
            texts.wallet_settings(tg_id),
            kb.settings(tg_id),
            "wallet_menu_id",
            "wallet_menu_id",
            "on_callback")


@Client.on_callback_query(Filters.create(lambda _, cb: cb.data.startswith("back_add_wallet")))
def back_add_wallet(cli, cb):
    tg_id = cb.from_user.id
    wallets = cache.get_user_wallets(tg_id)
    cache.change_user_flag(tg_id, "await_mnemonic", False)
    if len(wallets) == 0:
        return new_msg(cli, cb, tg_id,
                "Do you want to create a wallet or add an existing one",
                kb.first_start(),
                "wallet_menu_id",
                "wallet_menu_id",
                "on_callback")

    new_msg(cli, cb, tg_id,
            texts.add_wallet(tg_id),
            kb.add_wallet(tg_id),
            "wallet_menu_id",
            "wallet_menu_id",
            "on_callback")
