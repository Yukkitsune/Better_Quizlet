from aiogram.fsm.state import StatesGroup, State


class LearningStates(StatesGroup):
    choosing_deck = State()
    studying = State()
    awaiting_answer = State()
    feedback = State()
