#!/usr/bin/python
from aiogram.enums.content_type import ContentType
from aiogram import Bot, Dispatcher
from config import *
from aiogram.enums import ParseMode
from handlers import admin_handlers
from handlers import user_handlers
import asyncio

dp = Dispatcher()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)


async def main() -> None:
    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
