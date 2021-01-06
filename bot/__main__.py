import asyncio

from pyrogram import idle

from bot import mybot, startwebserver


async def main():
    await startwebserver()
    await mybot.start()
    await idle()
    await mybot.stop()

if __name__ == "__main__":
    asyncio.run(main())
