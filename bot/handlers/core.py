from aiogram import Router, types
from aiogram.filters import Command
import sqlite3
from bot.states import LearningStates
from bot.handlers.study import get_deck, _get_decks
from aiogram.fsm.context import FSMContext
import asyncio

router = Router()


@router.message(Command("start"))
async def start_handler(
    message: types.Message, db_conn: sqlite3.Connection, state: FSMContext
):
    await state.clear()
    await state.set_state(LearningStates.choosing_deck)

    decks = await asyncio.to_thread(_get_decks, db_conn)
    if not decks:
        await message.answer("Колод пока нет")
        return
    await message.answer("Привет! Выбери колоду:", reply_markup=get_deck(decks))
