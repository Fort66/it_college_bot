from aiogram.fsm.state import State, StatesGroup


class StartState(StatesGroup):
    start = State()
    teachers = State()
    students = State()
    exit = State()
