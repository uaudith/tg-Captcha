from bot.userAnswers import markCompleted
from ..captchaBot import mybot


async def onSuccess(userId: int, chaId: int):
    success = await mybot.unban_chat_member(chaId, userId)
    if success:
        msgId = await markCompleted(userId, chaId)
        return msgId
