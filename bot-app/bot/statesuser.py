from aiogram.fsm.state import State, StatesGroup


class TaskFinish(StatesGroup):
    task = State()
    number_of_task = State()


class Settings(StatesGroup):
    count_tasks = State()
    time_hour = State()
    time_minute = State()
    time_custom_minute = State()


class SendingMessage(StatesGroup):
    value = State()
    confirm_sending = State()
    image_id = State()
