import asyncio
import logging
from time import time

from pyrogram import Client
from pyrogram.methods.chats.iter_chat_members import Filters
from pyrogram.types import Message, ChatPermissions

from ..config import config
from ..helpers import get_buttons, mentionStr
from ..userAnswers import taskStorage, addTask
from ..captchaBot import mybot

logger = logging.getLogger(__name__)


async def handleNewMember(c: Client, msg: Message):
    user_id = msg.from_user.id
    chat_id = msg.chat.id
    logger.info("Handling new member %d joining in %d chat", user_id, chat_id)
    if user_id not in msg.new_chat_members and await isAdmin(user_id, chat_id):
        logging.info("admin %d added members", msg.from_user.id)
        return  # admin adding members

    await msg.chat.restrict_member(user_id, ChatPermissions())
    if (user_id, chat_id) in taskStorage:
        await msg.reply("Kicking this user ..\nHe left without verifying yet joined again now")
        await c.kick_chat_member(chat_id, msg.from_user.id, int(time() + config.KICK_TIME * 3600))
        return
    sendingStr = f"Wellcome {mentionStr(msg.from_user)} !\n " \
                 f"Please verify yourself within {config.MAX_TIME_TO_SOLVE} Seconds"
    if msg.from_user not in msg.new_chat_members:
        # nameConcat = ", ".join(x.first_name or x.last_name for x in msg.new_chat_members)
        sendingStr = f"{mentionStr(msg.from_user)}, You have to do the verification for the members you are adding"

    sent = await msg.reply_text(sendingStr, reply_markup=get_buttons(user_id, chat_id))
    task = timeOutTask(c, msg, sent, user_id)
    await addTask(user_id, chat_id, task)


async def timeOutTask(c, msg, sent, user_id):
    try:
        await asyncio.sleep(config.MAX_TIME_TO_SOLVE)
        await c.kick_chat_member(sent.chat.id, sent.from_user.id, int(time() + config.KICK_TIME * 3600))
        await sent.edit(f"{mentionStr(msg.from_user)} failed to verify. He can "
                        f"try again after {config.KICK_TIME} hours")
    except asyncio.CancelledError:
        logger.info("user %d has solved before the deadline", user_id)
        await sent.delete()
    finally:
        del taskStorage[(user_id, msg.chat.id)]


async def isAdmin(user: int, chat: int) -> bool:
    async for chatMem in mybot.iter_chat_members(chat, filter=Filters.ADMINISTRATORS):
        if chatMem.user.id == user:
            return True
    return False
