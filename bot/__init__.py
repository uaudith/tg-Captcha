import logging

from pyrogram import filters
from pyrogram.handlers import MessageHandler

from bot.captchaBot import mybot
from bot.handlers import handleNewMember, initMe, startCmd, helpCmd, botWasKicked
from bot.webServer import start as startwebserver

logging.basicConfig(level=logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
newMemberHandler = MessageHandler(handleNewMember, filters=filters.new_chat_members)
mybot.add_handler(newMemberHandler)
mybot.add_handler(MessageHandler(startCmd, filters=filters.command("start")))
mybot.add_handler(MessageHandler(helpCmd, filters=filters.command("help")))
# mybot.add_handler(MessageHandler(botWasKicked, filters=filters. & filters.me))
logging.info("Handlers added")
