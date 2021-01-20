from ..captchaBot import mybot
from pyrogram.methods.chats.iter_chat_members import Filters


async def isAdmin(user: int, chat: int) -> bool:
    async for chatMem in mybot.iter_chat_members(chat, filter=Filters.ADMINISTRATORS):
        if chatMem.user.id == user:
            return True
    return False
