from bot.userAnswers import markCompleted
from ..captchaBot import mybot
from ..helpers import mentionStr


async def onSuccess(userId: int, chaId: int):
    await markCompleted(userId, chaId)
    success = await mybot.unban_chat_member(chaId, userId)
    if success:
        cMem = await mybot.get_chat_member(chaId, userId)
        await mybot.send_message(chaId, f"{mentionStr(cMem.user)} verified Successfully")
