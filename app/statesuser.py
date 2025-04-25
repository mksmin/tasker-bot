from aiogram.fsm.state import StatesGroup, State


class TaskFinish(StatesGroup):
    task = State()
    number_of_task = State()


class Settings(StatesGroup):
    count_tasks = State()
    time_hour = State()
    time_minute = State()
