from aiogram.fsm.state import State, StatesGroup


class InterviewFlow(StatesGroup):
    choosing_position = State()
    choosing_level = State()
    waiting_answer = State()
    choosing_next = State()
