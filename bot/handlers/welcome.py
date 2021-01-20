from pyrogram import Client
from pyrogram.types import Message
from ..welcomeMsg import WelcomeMsg
from ..helpers import isAdmin


async def setWelcomeCmd(_: Client, m: Message):
    if not m.reply_to_message:
        await m.reply("⚠ You have to use this command as a reply to the Welcome message\n"
                      "Reffer /help to know about formatting in welcome message")
        return
    welcomeStr = m.reply_to_message.caption or m.reply_to_message.text
    if len(welcomeStr) > 1024:
        await m.reply("🚫 Maximum number of characters supported is 1024")
        return
    if not await isAdmin(m.from_user.id, m.chat.id):
        await m.reply("🚫 This command is only for the admins")
        return
    WelcomeMsg.storeWelcomeMsg(m.chat.id, welcomeStr)
    await m.reply("✔ Welcome message successfuly saved")


async def delWelcomeCmd(_: Client, m: Message):
    if not await isAdmin(m.from_user.id, m.chat.id):
        await m.reply("🚫 This command is only for the admins")
        return
    WelcomeMsg.clearWelcomeMsg(m.chat.id)
    await m.reply("✔ Welcome message removed successfuly")
