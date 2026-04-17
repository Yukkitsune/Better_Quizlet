from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from core import config
from db.connection import init_db, close_db
from bot.handlers.core import router
import asyncio


async def main():
    bot = Bot(token=config.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    conn = init_db()
    dp["db_conn"] = conn
    try:
        await dp.start_polling(bot)
    finally:
        close_db(conn)


if __name__ == "__main__":
    asyncio.run(main())
