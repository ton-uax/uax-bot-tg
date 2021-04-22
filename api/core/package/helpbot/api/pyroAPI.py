from pyrogram import Client

from django.conf import settings
from pyrogram import InlineKeyboardMarkup, InlineKeyboardButton


class HelpBot(Client):

    def __init__(self, session_name="session_helpbot"):
        super().__init__(session_name=session_name, api_id=settings.TG_API_ID, api_hash=settings.TG_API_HASH, bot_token=settings.TG_API_TOKEN)

    def send_msg(self, tg_id, text, open_wallet=False, wallet_id=False):
        app = self.start()

        try:
            if open_wallet:
                app.send_message(tg_id, text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Open", callback_data=f"open_wallet-{wallet_id}")]]))
            else:
                app.send_message(tg_id, text)
        except Exception as e:
            print(e)
        app.stop()
