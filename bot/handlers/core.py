from aiogram import Router, types
from aiogram.filters import Command
import sqlite3

router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message, db_conn: sqlite3.Connection):
    cursor = db_conn.execute("SELECT 1")
    cursor.fetchone()
    await message.answer("Бот запущен, БД подключена")
