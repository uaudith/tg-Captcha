from pyrogram import Client
from pyrogram.types import Message
from ..helpers import isAdmin
from ..chatSettings import chatSettings


async def showInfo(_: Client, m: Message):
    inputD = m.text.split(maxsplit=1)[-1]
    if inputD.lower() == 'off':
        data = False
    elif inputD.lower() == 'on':
        data = True
    else:
        await m.reply("🚫 wrong arguements\n"
                      "Correct arguements are `on` or `off`")
        return
    if not await isAdmin(m.from_user.id, m.chat.id):
        await m.reply("🚫 This command is only for the admins")
        return
    chatSettings(m.chat.id).setShowInfo(data)
    await m.reply("✔ Saved\n"
                  f"From now on i will {'' if data else 'not'} send "
                  f"messages like `verified in x seconds` or messages about failed users")
