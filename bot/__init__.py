import logging

from pyrogram import filters
from pyrogram.handlers import MessageHandler

from bot.config import config
from bot.captchaBot import mybot
from bot.handlers import handleNewMember, initMe, startCmd, helpCmd,\
    botWasKicked, setWelcomeCmd, showInfo, delWelcomeCmd
from bot.webServer import start as startwebserver
from bot.welcomeMsg import WelcomeMsg, LastWelcome, oldWelcomeDeleteService
from bot.helpers import smart_command
from bot.userAnswers import unmuteBeforeTerminatie


logging.basicConfig(level=logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

mybot.add_handler(MessageHandler(handleNewMember, filters=filters.new_chat_members))
mybot.add_handler(MessageHandler(startCmd, filters=smart_command('start')))
mybot.add_handler(MessageHandler(setWelcomeCmd, filters=smart_command('setWelcome') & ~filters.private))
mybot.add_handler(MessageHandler(delWelcomeCmd, filters=smart_command('delWelcome') & ~filters.private))
mybot.add_handler(MessageHandler(showInfo, filters=smart_command('showInfo') & ~filters.private))
mybot.add_handler(MessageHandler(helpCmd, filters=smart_command('help')))
# mybot.add_handler(MessageHandler(botWasKicked, filters=filters. & filters.me))

logging.info("Handlers added")
