import asyncio
import signal
from pyrogram import idle

from bot import mybot, startwebserver, initMe, WelcomeMsg, oldWelcomeDeleteService, \
    unmuteBeforeTerminatie


async def main():
    try:
        for signame in {'SIGINT', 'SIGTERM'}:
            loop.add_signal_handler(
                getattr(signal, signame),
                unmuteBeforeTerminatie)
    except NotImplementedError:
        pass
    [asyncio.create_task(task()) for task in (
        oldWelcomeDeleteService,
        WelcomeMsg.clear_welcome_cache_service)
     ]
    await startwebserver()
    await mybot.start()
    await initMe()
    await idle()
    await mybot.stop()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
