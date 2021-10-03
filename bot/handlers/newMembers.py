import asyncio
import logging
from time import time
from typing import Union

from pyrogram import Client
from pyrogram.errors import UserIdInvalid, ChatAdminRequired, UserAdminInvalid, ChatWriteForbidden, \
    MessageDeleteForbidden
from pyrogram.types import Message, ChatPermissions

from ..channelLoger import logInChannel
from ..config import config
from ..helpers import authUrlButtons, isAdmin, mentionStr, time_formatter
from ..userAnswers import taskStorage, addTask
from ..captchaBot import mybot
from ..welcomeMsg import WelcomeMsg, LastWelcome, getFillings
from ..failedUsers import FailedUsers
from ..chatSettings import chatSettings

logger = logging.getLogger(__name__)
me = None


async def initMe():
    global me
    me = await mybot.get_me()


async def introduceMe(msg):
    await msg.reply("Thank you for adding me 🙌\n\n"
                    "From now on i will protect your group from bots and spammers ⚔ \n\n"
                    "Make sure to promote me as an admin with ban and delete permission 🛡️ ")
    await logInChannel(f"Added to new group #{msg.chat.id}\n"
                       f"Chat name : `{msg.chat.title}`")


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
    try:
        await msg.chat.restrict_member(user_id, ChatPermissions())
    except ChatAdminRequired:
        try:
            await msg.reply("I need to be an admin to work properly")
        except ChatWriteForbidden:
            await msg.chat.leave()
        return
    try:
        await msg.delete()
    except MessageDeleteForbidden:
        pass
    if (user_id, chat_id) in taskStorage:
        # sent = await msg.reply("Kicking this user ..\nHe left without verifying yet joined again now")
        return
    sendingStr = f"Wellcome {mentionStr(msg.from_user)} !\n " \
                 f"Please verify yourself within {config.MAX_TIME_TO_SOLVE} Seconds"
    if msg.from_user not in msg.new_chat_members:
        # nameConcat = ", ".join(x.first_name or x.last_name for x in msg.new_chat_members)
        sendingStr = f"{mentionStr(msg.from_user)}, You have to do the verification for the members you are adding\n" \
                     f"Else you will be banned"

    sent = await msg.reply_text(sendingStr, reply_markup=authUrlButtons(chat_id))
    task = timeOutTask(c, msg, sent, user_id)
    await addTask(user_id, chat_id, task)


async def timeOutTask(c, msg, sent, user_id) -> Union[int, None]:
    startT = time()
    settings = chatSettings(msg.chat.id)
    settingsTask = asyncio.shield(
        asyncio.create_task(settings.getSettings())
    )
    try:
        await asyncio.sleep(config.MAX_TIME_TO_SOLVE)
        await settingsTask
        await tryToKick(c, msg, sent, sendAck=settings.showInfo)

    except asyncio.CancelledError:
        await settingsTask
        lastmsg = msg
        if settings.showInfo:
            lastmsg = await sent.edit(f"{mentionStr(msg.from_user)} #verified in `{time() - startT:.1f} seconds` ")
        else:
            await sent.delete()
        wcMsg: WelcomeMsg = WelcomeMsg.getWelcomeMsg(msg.chat.id)
        if wcMsg:
            msgText = wcMsg.caption.format_map(getFillings(msg))
            welcomeMessage = await lastmsg.reply(msgText, reply_markup=wcMsg.keyboardMarkup)
            # deletes previuos and keep this welcome as the last one
            await LastWelcome(msg.chat.id, welcomeMessage.message_id).setAsLast()
        logger.info("user %d has solved before the deadline", user_id)
        return lastmsg.message_id
    finally:
        del taskStorage[(user_id, msg.chat.id)]


async def tryToKick(c, msg, sent, sendAck=True) -> bool:
    try:
        failedUser = FailedUsers(msg.from_user.id)
        kickTime = config.KICK_TIME * 3600  # hours
        failedCount = await failedUser.getFailedCount()
        if failedCount > 2:
            kickTime *= 24 * failedCount  # days
        await c.kick_chat_member(msg.chat.id, msg.from_user.id, int(time() + kickTime))
        if sendAck:
            outStr = f"{mentionStr(msg.from_user)} failed to verify. They can" \
                     f" try again after {time_formatter(kickTime)}"
            if failedCount:
                outStr += f"\n`Failed attempts in a row: {failedCount}`"
            await sent.edit(outStr)
        else:
            await sent.delete()
        asyncio.create_task(failedUser.submit())
        return True
    except UserIdInvalid:
        logger.info("Seems user was banned by another admin or user left")
        return False
    except (ChatAdminRequired, UserAdminInvalid) as e:
        await sent.edit(str(e))
        return False
