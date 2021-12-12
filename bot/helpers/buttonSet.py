from pyrogram.types import InlineKeyboardMarkup, LoginUrl, InlineKeyboardButton

from bot.config import config


def authUrlButtons(chatID: int):
    loginUrl = LoginUrl(
        url=config.FQDN + f"/{chatID}",
        forward_text="why forward the message",
        bot_username=config.BOT_USERNAME)
    btn = InlineKeyboardButton(text="Verify", login_url=loginUrl)
    return InlineKeyboardMarkup([[btn]])
