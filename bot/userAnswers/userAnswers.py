import asyncio
import logging
from typing import Dict, Awaitable, Tuple

from bot import mybot
from bot.failedUsers import FailedUsers

taskStorage: Dict[Tuple[int, int], asyncio.Task] = {}
logger = logging.getLogger(__name__)


async def addTask(userId: int, chatId: int, task: Awaitable):
    asyncioTask = asyncio.create_task(task)
    taskStorage.update({(userId, chatId): asyncioTask})
    await asyncio.sleep(0.1)


async def markCompleted(userId: int, chatId: int):
    task = taskStorage[(userId, chatId)]
    task.cancel()
    return await task


def unmuteBeforeTerminatie():
    for (userId, chatId) in taskStorage.keys():
        asyncio.create_task(onSuccess(userId, chatId))
    logger.info("Unmuting Waiting users")


async def onSuccess(userId: int, chaId: int):
    success = await mybot.unban_chat_member(chaId, userId)
    if success:
        FailedUsers(userId).reset()
        msgId = await markCompleted(userId, chaId)
        return msgId
