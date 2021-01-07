import asyncio

from pyrogram import idle

from bot import mybot, startwebserver


async def main():
    await startwebserver()
    await mybot.start()
    await idle()
    await mybot.stop()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
