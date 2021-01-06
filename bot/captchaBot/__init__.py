from pyrogram import Client

from ..config import config

mybot = Client("captchaBot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)
