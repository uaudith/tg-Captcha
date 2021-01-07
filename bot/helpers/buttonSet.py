from pyrogram.types import InlineKeyboardButton as Btn, InlineKeyboardMarkup

from bot.config import config


def get_buttons(userId: int, chatId: int) -> InlineKeyboardMarkup:
    user_chat = str(userId)+'_'+str(chatId)
    return InlineKeyboardMarkup([
        [Btn("A", url=config.FQDN+f"/{user_chat}")]
        ])
