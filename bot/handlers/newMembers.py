import asyncio
import logging
from time import time

from pyrogram import Client
from pyrogram.errors import UserIdInvalid, ChatAdminRequired, UserAdminInvalid
from pyrogram.methods.chats.iter_chat_members import Filters
from pyrogram.types import Message, ChatPermissions

from ..config import config
from ..helpers import get_buttons, mentionStr
from ..userAnswers import taskStorage, addTask
from ..captchaBot import mybot

logger = logging.getLogger(__name__)
me = None


async def initMe():
    global me
    me = await mybot.get_me()


async def introduceMe(msg):
    await msg.reply("Thank you for adding me 🙌\n\n"
                    "From now on i will protect your group from bots and spammers ⚔ \n\n"
                    "Make sure to promote me as an admin with ban permission 🛡️ ")


async def handleNewMember(c: Client, msg: Message):
    user_id = msg.from_user.id
    chat_id = msg.chat.id
    if me in msg.new_chat_members:
        await introduceMe(msg)
        return
    logger.info("Handling new member %d joining in %d chat", user_id, chat_id)
    if user_id not in msg.new_chat_members and await isAdmin(user_id, chat_id):
        logging.info("admin %d added members", msg.from_user.id)
        return  # admin adding members

    await msg.chat.restrict_member(user_id, ChatPermissions())
    if (user_id, chat_id) in taskStorage:
        sent = await msg.reply("Kicking this user ..\nHe left without verifying yet joined again now")
        await tryToKick(c, msg, sent)
        return
    sendingStr = f"Wellcome {mentionStr(msg.from_user)} !\n " \
                 f"Please verify yourself within {config.MAX_TIME_TO_SOLVE} Seconds"
    if msg.from_user not in msg.new_chat_members:
        # nameConcat = ", ".join(x.first_name or x.last_name for x in msg.new_chat_members)
        sendingStr = f"{mentionStr(msg.from_user)}, You have to do the verification for the members you are adding\n" \
                     f"Else you will be banned"

    sent = await msg.reply_text(sendingStr, reply_markup=get_buttons(user_id, chat_id))
    task = timeOutTask(c, msg, sent, user_id)
    await addTask(user_id, chat_id, task)


async def timeOutTask(c, msg, sent, user_id):
    try:
        await asyncio.sleep(config.MAX_TIME_TO_SOLVE)
        if await tryToKick(c, msg, sent):
            await sent.reply(f"{mentionStr(msg.from_user)} failed to verify. He can "
                             f"try again after {config.KICK_TIME} hours")
    except asyncio.CancelledError:
        logger.info("user %d has solved before the deadline", user_id)
    finally:
        await sent.delete()
        del taskStorage[(user_id, msg.chat.id)]


async def tryToKick(c, msg, sent) -> bool:
    try:
        await c.kick_chat_member(msg.chat.id, msg.from_user.id, int(time() + config.KICK_TIME * 3600))
        return True
    except UserIdInvalid:
        logger.info("Seems user was banned by another admin or user left")
        return False
    except (ChatAdminRequired, UserAdminInvalid) as e:
        await sent.edit(str(e))
        return False


async def isAdmin(user: int, chat: int) -> bool:
    async for chatMem in mybot.iter_chat_members(chat, filter=Filters.ADMINISTRATORS):
        if chatMem.user.id == user:
            return True
    return False
