from pyrogram import Client
from pyrogram.types import Message


async def startCmd(_: Client, m: Message):
    await m.reply("Captcha Bot is Running")


async def helpCmd(_: Client, m: Message):
    await m.reply("It is simple 🙂\n\n"
                  "Add me to a group and make me an **admin** 👑\n"
                  "I will stop spammers and bots with captchas 🛡️")
