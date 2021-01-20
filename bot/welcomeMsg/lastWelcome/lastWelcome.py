from concurrent.futures import ThreadPoolExecutor
import logging
import sqlite3
import asyncio
from time import time
from functools import partial
from ...captchaBot import mybot
from ...config import config

LOGGER = logging.getLogger(__name__)
LOGGER.info("Setting up the databse for last welcome")
_conn = sqlite3.connect(":memory:", check_same_thread=False)
_cur = _conn.cursor()
_cur.execute("""create table if not exists lastWcMsg(chatId integer primary key , msgId integer, initTime REAL)""")
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


class LastWelcome:
    def __init__(self, chatId: int, messageId: int):
        self.chatId = chatId
        self.messageId = messageId

    async def setAsLast(self):
        loop = asyncio.get_running_loop()
        cur: sqlite3.Cursor = await loop.run_in_executor(None,
                                                         partial(
                                                             performQuery,
                                                             """select msgId from lastWcMsg where chatId=?""",
                                                             self.chatId
                                                         ))
        result = cur.fetchone()
        if result:
            (lastWcMsg,) = result
            await self.__class__(self.chatId, lastWcMsg).delWelcomeMessage()
        loop.run_in_executor(worker,
                             partial(
                                 performQueryAndCommit,
                                 """INSERT or replace into lastWcMsg(chatId, msgId, initTime) values(?,?,?)""",
                                 self.chatId,
                                 self.messageId,
                                 time()
                             ))

    async def delWelcomeMessage(self):
        return await mybot.delete_messages(self.chatId, self.messageId)


async def oldWelcomeDeleteService():
    while True:
        LOGGER.debug("starting old welcome deleting service")
        await asyncio.sleep(config.WELCOME_LIFETIME)
        loop = asyncio.get_running_loop()
        now = time()
        cur: sqlite3.Cursor = await \
            loop.run_in_executor(None,
                                 partial(
                                     performQuery,
                                     """select chatId, msgId from lastWcMsg where ? - initTime > ?""",
                                     now,
                                     config.WELCOME_LIFETIME
                                 ))
        a = cur.fetchall()
        loop.run_in_executor(worker,
                             partial(
                                 performQueryAndCommit,
                                 """delete from lastWcMsg where ? - initTime > ?""",
                                 now,
                                 config.WELCOME_LIFETIME
                             ))

        if a:
            for row in a:
                LOGGER.debug("deleting welcome message in %d chat %d msgid", *row)
                await LastWelcome(*row).delWelcomeMessage()
            LOGGER.info("deleted %d welcome", len(a))
