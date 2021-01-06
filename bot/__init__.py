import logging

from pyrogram import filters
from pyrogram.handlers import MessageHandler

from bot.captchaBot import mybot
from bot.handlers import handleNewMember
from bot.webServer import start as startwebserver

logging.basicConfig(level=logging.INFO)
newMemberHandler = MessageHandler(handleNewMember, filters=filters.new_chat_members)
mybot.add_handler(newMemberHandler)
logging.info("NewMembers handler added")
