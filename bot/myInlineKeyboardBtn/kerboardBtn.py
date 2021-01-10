from typing import Union
from pyrogram import types, raw
from pyrogram.raw.base import InputUser

from pyrogram.types import InlineKeyboardButton


class myInlineKeyboardButton(InlineKeyboardButton):
    def __init__(
            self,
            text: str,
            callback_data: Union[str, bytes] = None,
            url: str = None,
            switch_inline_query: str = None,
            switch_inline_query_current_chat: str = None,
            callback_game: "types.CallbackGame" = None,
            fwd_text: str = None,
            bot: InputUser = None
    ):
        super().__init__(text, callback_data, url, switch_inline_query, switch_inline_query_current_chat, callback_game)

        self.fwd_text = fwd_text
        self.bot = bot

    @staticmethod
    def read(o):
        if isinstance(o, raw.types.InputKeyboardButtonUrlAuth):
            return myInlineKeyboardButton(
                text=o.text,
                url=o.url,
                fwd_text=o.fwd_text,
                bot=o.bot
            )
        return super(myInlineKeyboardButton, myInlineKeyboardButton).read(o)

    def write(self):
        if self.bot is not None:
            return raw.types.InputKeyboardButtonUrlAuth(text=self.text, url=self.url,
                                                        fwd_text=self.fwd_text, bot=self.bot)
        return super(myInlineKeyboardButton, self).write()
