import asyncio
import logging
import sqlite3
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial

LOGGER = logging.getLogger(__name__)
LOGGER.info("Setting up the databse for chat settings")
_conn = sqlite3.connect("db/ucaptcha.db", check_same_thread=False)
_cur = _conn.cursor()
_cur.execute("""
create table if not exists chatSettings(
chatId integer primary key ,
showInfo boolean default 1 check ( showInfo in (0,1) ),
kickTime1 integer,
kicktime2 integer
)""")
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


class chatSettings:
    def __init__(self, chatId):
        self.chatId = chatId
        self.showInfo = None

    def setShowInfo(self, state: bool):
        loop = asyncio.get_running_loop()
        loop.run_in_executor(
            worker,
            partial(
                performQueryAndCommit,
                """insert or replace into chatSettings(chatId, showInfo)
                values(?, ?)""",
                self.chatId,
                1 if state else 0
            ))

    async def getSettings(self):
        loop = asyncio.get_running_loop()
        cur: sqlite3.Cursor = await loop.run_in_executor(
            None,
            partial(
                performQuery,
                """select showInfo from chatSettings
                where chatId=?""",
                self.chatId
            ))
        result = cur.fetchone()
        showInfo = 1
        if result:
            (showInfo,) = result
        setattr(self, 'showInfo', showInfo)
