from pyrogram import Client
from pyrogram.types import Message

from ..channelLoger import logInChannel


async def botWasKicked(_: Client, m: Message):
    await logInChannel(f"Got kicked from group #{m.chat.id}\n"
                       f"Chat name : `{m.chat.title}`")
