from ..captchaBot import mybot
from ..config import config


async def logInChannel(text: str):
    if not bool(config.LOG_CHANNEL):
        return
    await mybot.send_message(config.LOG_CHANNEL, text)
