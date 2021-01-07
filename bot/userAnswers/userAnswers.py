import asyncio
from typing import Dict, Awaitable, Tuple

taskStorage: Dict[Tuple[int, int], asyncio.Task] = {}


async def addTask(userId: int, chatId: int, task: Awaitable):
    asyncioTask = asyncio.create_task(task)
    taskStorage.update({(userId, chatId): asyncioTask})
    await asyncio.sleep(0.1)


async def markCompleted(userId: int, chatId: int):
    task = taskStorage[(userId, chatId)]
    task.cancel()
