from pyrogram.raw.types import InputUserSelf
from pyrogram.types import InlineKeyboardMarkup

from bot.config import config
from ..myInlineKeyboardBtn import myInlineKeyboardButton


def authUrlButtons(chatID: int):
    btn = myInlineKeyboardButton(text="Verify", url=config.FQDN+f"/{chatID}",
                                 fwd_text="why forward the message", bot=InputUserSelf())
    return InlineKeyboardMarkup([[btn]])
