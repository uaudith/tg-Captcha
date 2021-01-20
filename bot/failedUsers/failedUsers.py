import asyncio
import functools
import logging
import sqlite3
from concurrent.futures import ThreadPoolExecutor

LOGGER = logging.getLogger(__name__)
LOGGER.info("Setting up the databse for failed users")
_conn = sqlite3.connect('db/ucaptcha.db', check_same_thread=False)
_cur = _conn.cursor()
_cur.execute("""create table if not exists failedUsers(userid integer primary key , fCount integer default 1)""")
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


class FailedUsers:
    def __init__(self, userId: int):
        self.userId = userId
        # self.failCount = failCount

    async def submit(self):
        loop = asyncio.get_running_loop()
        cur: sqlite3.Cursor = await loop.run_in_executor(worker,
                                                         functools.partial(
                                                             performQueryAndCommit,
                                                             """update failedUsers
                                                 set fCount= fCount+1
                                                 where userid=?""",
                                                             self.userId,
                                                         ))
        if cur is None or cur.rowcount <= 0:
            loop.run_in_executor(worker,
                                 functools.partial(
                                     performQueryAndCommit,
                                     """insert or ignore into failedUsers(userid, fCount) 
                                     VALUES(?,1)""",
                                     self.userId,
                                 ))

    async def getFailedCount(self):
        loop = asyncio.get_running_loop()
        cur = await loop.run_in_executor(worker,
                                         functools.partial(
                                             performQuery,
                                             """select fCount from failedUsers where userid=?""",
                                             self.userId)
                                         )
        fCount = cur.fetchone()
        if fCount:
            (fCount,) = fCount
            return fCount
        return 0

    def reset(self):
        loop = asyncio.get_running_loop()
        loop.run_in_executor(worker,
                             functools.partial(
                                 performQueryAndCommit,
                                 """delete from failedUsers where userid=?""",
                                 self.userId)
                             )
