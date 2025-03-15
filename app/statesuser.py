from aiogram.fsm.state import StatesGroup, State


class TaskFinish(StatesGroup):
    task = State()
    number_of_task = State()
