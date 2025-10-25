from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import commands, media
import asyncio


bot = Bot(TOKEN, timeout=10)
dp = Dispatcher()


async def main():
    dp.include_router(commands.router)
    dp.include_router(media.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
