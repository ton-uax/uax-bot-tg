from pyrogram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from core.apps.account import models as account_models
from .api.pyroAPI import HelpBot


def send_msg(tg_id: int, text: str, session_name: str = "defultsess"):
    client = HelpBot(session_name=session_name)
    client.send_msg(tg_id, text)


def broadcast(users: iter, message: str, keyboard: str, forced_for_admin=False, session_name="session_broadcast", **kwargs):
    client = HelpBot(session_name=session_name)
    client.start()
    blocked_bot_objs = []
    for user in users:
        try:
            if keyboard == "will_invite":
                # if forced_for_admin:
                #     if user.admin:
                #         message += "\n\n❗️ Этот пользователь повторный раз поставлен в очередь!"
                kb = InlineKeyboardMarkup([[InlineKeyboardButton("Я готов", callback_data=f"will_invite")]])
                client.send_message(user.tg_id, message, reply_markup=kb)

            elif keyboard == "wakeup":
                kb = InlineKeyboardMarkup([[InlineKeyboardButton("Я тут ✌️", callback_data=f"wakeup")]])
                client.send_message(user.tg_id, message, reply_markup=kb)
            elif keyboard == "none":
                client.send_message(user.tg_id, message)
        except:
            user.blocked_bot = True
            blocked_bot_objs.append(user)
            continue

    client.stop()
    if len(blocked_bot_objs) > 0:
        account_models.TelegramAccount.objects.bulk_update(blocked_bot_objs, ["blocked_bot"])
        return blocked_bot_objs


def get_tg_user(tg_id: int or str):
    client = HelpBot(session_name="get_tg_user_session")
    client.start()

    tg_user = client.get_users(tg_id)
    user = {
        "id": tg_user.id,
        "username": "[отсутствует]",
        "first_name": "[отсутствует]",
        "last_name": "[отсутствует]",
    }

    if tg_user.username:
        user["username"] = tg_user.username

    if tg_user.first_name:
        user["first_name"] = tg_user.first_name

    if tg_user.last_name:
        user["last_name"] = tg_user.last_name
    client.stop()
    return user
