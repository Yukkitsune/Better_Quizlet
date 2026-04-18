from bot.states import LearningStates
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
import sqlite3
import asyncio
from db.queries import get_due_cards


router = Router()


def _get_decks(conn: sqlite3.Connection):
    return conn.execute("SELECT id, name FROM decks").fetchall()


def get_deck(decks):
    kb = InlineKeyboardBuilder()
    for deck_id, deck_name in decks:
        kb.button(text=deck_name, callback_data=f"deck:{deck_id}")
    return kb.adjust(len(decks)).as_markup()


@router.message(LearningStates.choosing_deck)
async def choosing_deck_handler(message: Message, db_conn: sqlite3.Connection):
    decks = await asyncio.to_thread(_get_decks, db_conn)
    if not decks:
        await message.answer("Колод пока нет.")
        return
    await message.answer("Выберите тематику колоды", reply_markup=get_deck(decks))


@router.callback_query(F.data.startswith("deck:"))
async def callback_handler(
    callback: CallbackQuery, state: FSMContext, db_conn: sqlite3.Connection
):
    await callback.answer()
    deck_id = int(callback.data.split(":")[1])
    await state.update_data(deck_id=deck_id)
    await state.set_state(LearningStates.studying)
    user_id = callback.from_user.id

    due_cards = await asyncio.to_thread(get_due_cards, db_conn, user_id, limit=1)
    if not due_cards:
        await callback.message.answer("Выучено в колоде")
        await state.clear()
        return
    card = due_cards[0]
    await state.update_date(current_card_id=card["id"])
    await callback.message.answer(f"🇬🇧 Слово: **{card['front']}**\n\n_Введи перевод:_")
