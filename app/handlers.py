# import from lib
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app import statesuser as st
from app import keyboards as kb

# import from modules
from database import Task
from database import requests as rq

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.get_user_by_tgid(message.from_user.id)
    await message.answer("Привет! Добавляй задачи, а я буду каждый день присылать 5 случайных! ")


async def send_daily_tasks(user_tgid: int, bot: Bot) -> None:
    tasks: list[Task] = await rq.get_list_of_random_tasks(used_tg=user_tgid)
    list_of_tasks = [task.text_task for task in tasks]

    if len(list_of_tasks) <= 0:
        await bot.send_message(
            chat_id=user_tgid,
            text="У вас нету тасок на сегодня")
        return

    stroke_tasks = '\n'.join(f'{i}. {task}' for i, task in enumerate(list_of_tasks, 1))
    msg_to_send = (f'Доброе утро, вот твои таски на сегодня:\n\n'
                   f'{stroke_tasks}')

    await bot.send_message(chat_id=user_tgid, text=msg_to_send, reply_markup=kb.finishing_task)


@router.message(Command('daily'))
async def cmd_daily_tasks(message: Message):
    await send_daily_tasks(
        user_tgid=message.from_user.id,
        bot=message.bot
    )


@router.callback_query(F.data == 'my_tasks')
@router.message(Command('my'))
async def cmd_my_tasks(message: Message | CallbackQuery):
    user_tg_id = message.from_user.id

    if isinstance(message, CallbackQuery):
        await message.answer('Все задачи ')
        message = message.message

    tasks: list[Task] = await rq.get_list_of_all_tasks(user_tg=user_tg_id)

    list_of_tasks = [task.text_task for task in tasks]

    if len(list_of_tasks) <= 0:
        await message.answer("У тебя нету тасок")
        return

    stroke_tasks = '\n'.join(f'{i}. {task}' for i, task in enumerate(list_of_tasks, 1))
    msg_to_send = (f'Вот твои таски:\n\n'
                   f'{stroke_tasks}')

    await message.answer(msg_to_send, reply_markup=kb.finishing_task)


@router.callback_query(F.data == 'finish_task')
async def cmd_finish_task(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Начинаю...')
    await state.set_state(st.TaskFinish.task)

    tasks: list[Task] = await rq.get_list_of_all_tasks(user_tg=callback.from_user.id)
    list_of_tasks = [task for task in tasks]

    if len(list_of_tasks) <= 0:
        await callback.message.answer("У тебя нету тасок")
        await state.clear()
        return

    await state.update_data(task=list_of_tasks)

    stroke_tasks = '\n'.join(f'{i}. {task.text_task}' for i, task in enumerate(list_of_tasks, 1))
    msg_to_send = (f'Вот твои таски:\n\n'
                   f'{stroke_tasks}')

    await callback.message.answer(msg_to_send)
    await callback.message.answer('Пришли мне номер таски, которую хочешь завершить')


@router.message(F.text.regexp(r"^\d+$"),
                st.TaskFinish.task)
async def finished_task(message: Message, state: FSMContext):
    await state.update_data(number_of_task=message.text)
    data = await state.get_data()

    if int(data['number_of_task']) > len(data['task']) or int(data['number_of_task']) < 1:
        await message.answer('Такой таски нету!')
        return

    task: Task = data['task'][int(data['number_of_task']) - 1]

    await rq.finish_task(task=task)
    await message.answer(f"Удалил таску: \n\n"
                         f"{task.text_task}")


@router.message(F.text)
async def user_add_task(message: Message, state: FSMContext):
    await state.clear()

    task_added = await rq.add_task(
        user_tg=message.from_user.id,
        user_text=message.text
    )

    if task_added:
        await message.answer(f"Добавил таску: \n\n"
                             f"{message.text}",
                             reply_markup=kb.list_of_tasks)
    else:
        await message.answer(f"Возникла ошибка")
