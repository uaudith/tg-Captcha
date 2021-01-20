import functools
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Union
from time import time
from pyrogram.types import InlineKeyboardMarkup
import asyncio
from .parseButtons import parse_buttons
import sqlite3
from bot.config import config
import logging

LOGGER = logging.getLogger(__name__)
CACHED_WELCOME_MESSAGES: Dict[int, Union['WelcomeMsg', None]] = {}
LOGGER.info("Setting up the databse for welcome messages")
_conn = sqlite3.connect('db/ucaptcha.db', check_same_thread=False)
_cur = _conn.cursor()
_cur.execute("""create table if not exists wcMsg(chatid integer primary key , string char(1024))""")
_conn.commit()
worker = ThreadPoolExecutor(max_workers=1)


def performQuery(sqlString, *args):
    return _cur.execute(
        sqlString,
        (*args,)
    )


def performQueryAndCommit(sqlString, *args):
    performQuery(sqlString, *args)
    _conn.commit()


class WelcomeMsg:
    def __init__(self, caption, keyboardMarkup, chatId):
        self.caption: str = caption
        self.keyboardMarkup: InlineKeyboardMarkup = keyboardMarkup
        self.chatId: int = chatId
        self._time = time()

    @classmethod
    def new(cls, string: str, chatId: int):
        text, btns = parse_buttons(string)
        return cls(
            text,
            btns,
            chatId,
        )

    @classmethod
    def storeWelcomeMsg(cls, chatId, payload):
        loop = asyncio.get_running_loop()
        loop.run_in_executor(worker,
                             functools.partial(
                                 performQueryAndCommit,
                                 """insert or replace into wcMsg(chatid, string) values (?, ?)""",
                                 chatId,
                                 payload)
                             )
        if chatId in CACHED_WELCOME_MESSAGES:
            CACHED_WELCOME_MESSAGES.update({chatId: cls.new(payload, chatId)})
        LOGGER.info("New welcome message set in chat %d", chatId)

    @staticmethod
    def clearWelcomeMsg(chatId: int):
        loop = asyncio.get_running_loop()
        loop.run_in_executor(worker,
                             functools.partial(
                                 performQueryAndCommit,
                                 """delete from wcMsg where chatid=?""",
                                 chatId)
                             )
        if chatId in CACHED_WELCOME_MESSAGES:
            del CACHED_WELCOME_MESSAGES[chatId]
        LOGGER.info("Welcome message cleared in chat %d", chatId)

    @classmethod
    async def _fetchWelcome(cls, chatId: int):
        loop = asyncio.get_running_loop()
        cur = await loop.run_in_executor(None,
                                         functools.partial(
                                             performQuery,
                                             """select string from wcMsg where chatid=?""",
                                             chatId)
                                         )
        welcomeMessage = cur.fetchone()
        if welcomeMessage:
            (welcomeMessage,) = welcomeMessage
            CACHED_WELCOME_MESSAGES.update({chatId: cls.new(welcomeMessage, chatId)})

    @classmethod
    def fetchWelcome(cls, chatId: int):
        if chatId in CACHED_WELCOME_MESSAGES:
            LOGGER.info("Welcome message for chat %d is already in memory", chatId)
            if CACHED_WELCOME_MESSAGES[chatId]:
                CACHED_WELCOME_MESSAGES[chatId].setTime()
        else:
            LOGGER.info("Welcome message fetched to mem for chat %d", chatId)
            CACHED_WELCOME_MESSAGES.update({chatId: None})
            asyncio.create_task(cls._fetchWelcome(chatId))

    def setTime(self):
        self._time = time()

    @staticmethod
    def getWelcomeMsg(chatId: int):
        test = CACHED_WELCOME_MESSAGES.get(
            chatId, None)
        return test

    @staticmethod
    async def clear_welcome_cache_service():
        while True:
            LOGGER.debug("starting welcome cache cleaning service")
            await asyncio.sleep(config.MAX_TIME_TO_SOLVE)
            for chatId in list(CACHED_WELCOME_MESSAGES.keys()):
                wcMsg = CACHED_WELCOME_MESSAGES[chatId]
                if wcMsg and time() - wcMsg._time > config.MAX_TIME_TO_SOLVE:
                    del CACHED_WELCOME_MESSAGES[chatId]
                await asyncio.sleep(0.1)
