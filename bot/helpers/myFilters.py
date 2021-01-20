from ..config import config
from pyrogram import filters


def smart_command(command: str):
    return filters.command(command) | filters.command(command + f'@{config.BOT_USERNAME}')
