# import from lib
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import time
from sqlalchemy import select

# import from modules
from app import statesuser as st, send_daily_tasks
from app import keyboards as kb
from . import update_schedule
from config import logger
from database import Task, User, user_settings_ctx, SettingsRepo, db_helper
from database import requests as rq
from database.models import UserSettings
from database.crud import crud_manager

# globals
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_data = {
        "user_tg": message.from_user.id,
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name,
        "username": message.from_user.username,
    }

    await crud_manager.user.create_user(user_data=user_data)
    await message.answer("Привет! Добавляй афоризмы, а я буду каждый день присылать тебе 5 случайных! ")


@router.message(Command('daily'))
async def cmd_daily_tasks(message: Message):
    user_tgid = message.from_user.id

    settings = await rq.get_user_settings(user_tg=user_tgid)

    tasks = await crud_manager.task.get_random_tasks(user_tg=user_tgid, count=settings.count_tasks)

    if len(tasks) <= 0:
        logger.info(f'No daily tasks to send to user %d', user_tgid)
        await message.answer("У тебя нет сохраненных текстов")
        return

    stroke_tasks = '\n'.join(f'{i}. {task.text_task}' for i, task in enumerate(tasks, 1))
    logger.info(f"Daily tasks: \n%s", stroke_tasks)
    msg_to_send = (f'Доброе утро, вот твои аффирмации на сегодня:\n\n'
                   f'{stroke_tasks}')

    await message.answer(text=msg_to_send, reply_markup=kb.finishing_task)
    logger.info(f'Daily tasks sent to user %d', user_tgid)


@router.callback_query(F.data == 'my_tasks')
@router.message(Command('my'))
async def cmd_my_tasks(message: Message | CallbackQuery):
    user_tg_id = message.from_user.id

    if isinstance(message, CallbackQuery):
        await message.answer('Все тексты')
        message = message.message

    tasks: list[Task] = await rq.get_list_of_all_tasks(user_tg=user_tg_id)

    list_of_tasks = [task.text_task for task in tasks]

    if len(list_of_tasks) <= 0:
        await message.answer("У тебя нет сохраненных текстов")
        return

    stroke_tasks = '\n'.join(f'{i}. {task}' for i, task in enumerate(list_of_tasks, 1))
    msg_to_send = (f'Вот твои аффирмации:\n\n'
                   f'{stroke_tasks}')

    await message.answer(msg_to_send, reply_markup=kb.finishing_task)


@router.callback_query(F.data == 'finish_task')
async def cmd_finish_task(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Начинаю...')
    await state.set_state(st.TaskFinish.task)

    tasks: list[Task] = await rq.get_list_of_all_tasks(user_tg=callback.from_user.id)
    list_of_tasks = [task for task in tasks]

    if len(list_of_tasks) <= 0:
        await callback.message.answer("У тебя нет сохраненных текстов")
        await state.clear()
        return

    await state.update_data(task=list_of_tasks)

    stroke_tasks = '\n'.join(f'{i}. {task.text_task}' for i, task in enumerate(list_of_tasks, 1))
    msg_to_send = (f'Вот твои аффирмации:\n\n'
                   f'{stroke_tasks}')

    await callback.message.answer(msg_to_send)
    await callback.message.answer('Пришли мне номер аффирмации, которую хочешь удалить')


@router.message(F.text.regexp(r"^\d+$"),
                st.TaskFinish.task)
async def finished_task(message: Message, state: FSMContext):
    await state.update_data(number_of_task=message.text)
    data = await state.get_data()

    if int(data['number_of_task']) > len(data['task']) or int(data['number_of_task']) < 1:
        await message.answer('Ты ошибся номером, такой аффирмации нет. Пришли еще раз')
        return

    task: Task = data['task'][int(data['number_of_task']) - 1]

    await rq.finish_task(task=task)
    await state.clear()
    await message.answer(f"Удалил аффирмацию: \n\n"
                         f"{task.text_task}",
                         reply_markup=kb.list_of_tasks)


@router.message(Command('settings'))
async def cmd_settings(message: Message, state: FSMContext):
    await state.clear()
    repo: SettingsRepo = user_settings_ctx.get()
    user = await crud_manager.user.get_user(user_tg=message.from_user.id)

    n = await repo.get(user.id)

    if not n:
        logger.debug("User has no settings. Creating new one...")
        await repo.set(user_id=user.id)
        n = await repo.get(user.id)

    await message.answer(f"<b>Текущие настройки</b>\n\n"
                         f"<b>{n.count_tasks}</b> — столько отправляется тебе аффирмаций в день\n"
                         f"<b>{n.send_time.strftime('%H:%M')} (мск)</b> — время отправки\n",
                         reply_markup=kb.settings_start)


@router.callback_query(F.data == 'change_settings')
async def cmd_change_settings(callback: CallbackQuery):
    await callback.message.edit_text('Выбери, что хочешь изменить', reply_markup=kb.settings_change)


@router.callback_query(F.data == 'change_amount')
async def cmd_change_amount(callback: CallbackQuery, state: FSMContext):
    await state.set_state(st.Settings.count_tasks)
    user = await crud_manager.user.get_user(user_tg=callback.from_user.id)
    async for session in db_helper.session_getter():
        query = select(UserSettings).where(UserSettings.user_id == user.id)
        executed = await session.execute(query)
        settings = executed.scalar_one()

    await callback.message.edit_text(f'Отправь число, которое должно быть меньше или равно 5 и больше 0'
                                     f'\nСейчас у тебя {settings.count_tasks} аффирмаций')


@router.message(st.Settings.count_tasks, F.text.regexp(r"^\d+$"))
async def cmd_change_amount(message: Message, state: FSMContext):
    if int(message.text) > 5 or int(message.text) < 1:
        await message.answer('Ты ошибся, число должно быть меньше или равно 5 и больше 0')
    else:
        user = await crud_manager.user.get_user(user_tg=message.from_user.id)

        await state.update_data(count_tasks=message.text)
        data = await state.get_data()
        try:
            async for session in db_helper.session_getter():
                query = select(UserSettings).where(UserSettings.user_id == user.id)
                executed = await session.execute(query)
                user_setting = executed.scalar_one()
                user_setting.count_tasks = int(data['count_tasks'])
                session.add(user_setting)
                await session.commit()

            await message.answer(f"Установил число аффирмаций: {data['count_tasks']}")
            await state.clear()

        except Exception as e:
            await message.answer('Ошибка при изменении настроек, {e}')
            await state.clear()
            return


@router.callback_query(F.data == 'change_time')
async def cmd_change_time(callback: CallbackQuery, state: FSMContext):
    await state.set_state(st.Settings.time_hour)
    user = await crud_manager.user.get_user(user_tg=callback.from_user.id)

    async for session in db_helper.session_getter():
        query = select(UserSettings).where(UserSettings.user_id == user.id)
        executed = await session.execute(query)
        settings = executed.scalar_one()

    await callback.message.edit_text(f'Отправь число от 0 до 23, это будет час отправки аффирмаций',
                                     f'\nСейчас время отправки {settings.send_time} ')


@router.message(st.Settings.time_hour, F.text.regexp(r"^\d+$"))
async def cmd_change_amount(message: Message, state: FSMContext):
    if int(message.text) > 23 or int(message.text) < 0:
        await message.answer('Ошибка, число должно быть меньше или равно 23 и больше 0')
    else:
        await state.update_data(time_hour=message.text)
        data = await state.get_data()
        try:
            await message.answer(f"Установил час отправки аффирмаций: {data['time_hour']}, теперь отправь минуты")
            await state.set_state(st.Settings.time_minute)

        except Exception as e:
            await message.answer('Ошибка при изменении настроек, {e}')
            await state.clear()
            return


@router.message(st.Settings.time_minute, F.text.regexp(r"^\d+$"))
async def cmd_change_amount(message: Message, state: FSMContext):
    if int(message.text) > 59 or int(message.text) < 0:
        await message.answer('Ошибка, число должно быть меньше или равно 59 и больше 0')
        return

    await state.update_data(time_minute=message.text)
    data = await state.get_data()
    new_time = time(hour=int(data['time_hour']), minute=int(data['time_minute']))

    user = await crud_manager.user.get_user(user_tg=message.from_user.id)

    try:
        async for session in db_helper.session_getter():
            query = select(UserSettings).where(UserSettings.user_id == user.id)
            executed = await session.execute(query)
            user_setting = executed.scalar_one()
            user_setting.send_time = new_time
            session.add(user_setting)
            await session.commit()

        await update_schedule(
            user_tg_id=message.from_user.id,
            new_time=new_time,
            bot=message.bot,
        )

        await message.answer(
            f"Установил время отправки аффирмаций: {new_time} (мск). Проверь настройки командой /settings")
        await state.set_state(st.Settings.time_minute)

    except Exception as e:
        logger.error(f"Ошибка при изменении настроек: {e}", exc_info=True)
        await message.answer(f'Ошибка при изменении настроек, {e}')
        await state.clear()
        return


@router.callback_query(F.data == 'back_to_settings')
async def cmd_back_to_settings(callback: CallbackQuery):
    await callback.message.edit_text('Ничего менять не будем. Вызови команду /settings, чтобы вернуться к настройкам')


@router.message(F.text)
async def user_add_task(message: Message, state: FSMContext):
    await state.clear()

    user_data = {
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name,
        "username": message.from_user.username,
    }
    # TODO: сделать метод для crud_manager на обновление данных пользователя
    # TODO: и заменить метод get_user_by_tgid на него
    await rq.get_user_by_tgid(message.from_user.id, user_data=user_data)

    task_added = await crud_manager.task.create_task(
        task_text=message.text,
        user_tg=message.from_user.id,
    )

    if task_added:
        await message.answer(f"Добавил аффирмацию: \n\n"
                             f"{task_added.text_task}",
                             reply_markup=kb.list_of_tasks)
    else:
        await message.answer(f"Возникла ошибка")
