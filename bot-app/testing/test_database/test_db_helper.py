# from collections.abc import AsyncGenerator
#
# import pytest
# import pytest_asyncio
# from sqlalchemy import text
#
# from database import Base
# from database.crud.managers.base import logger
# from database.db_helper import DatabaseHelper
#
#
# @pytest_asyncio.fixture()
# async def db_helper() -> AsyncGenerator[DatabaseHelper, None]:
#     """Сырой engine для работы с сессиями БД, без создания таблиц"""
#     helper = DatabaseHelper(url="sqlite+aiosqlite:///:memory:", echo=False)
#     yield helper
#     await helper.dispose()
#
#
# @pytest_asyncio.fixture()
# async def db_helper_with_tables(
#     db_helper: DatabaseHelper,
# ) -> AsyncGenerator[DatabaseHelper, None]:
#     """Сначала создаем таблицы, потом удаляем"""
#     async with db_helper.engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#
#     yield db_helper
#
#     async with db_helper.engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#
#
# @pytest.mark.asyncio
# async def test_engine_created(db_helper: DatabaseHelper) -> None:
#     assert db_helper.engine is not None
#     assert db_helper.session_factory is not None
#
#
# @pytest.mark.asyncio
# async def test_session_can_execute_query(db_helper: DatabaseHelper) -> None:
#     async for session in db_helper.session_getter():
#         result = await session.execute(text("SELECT 1"))
#         value = result.scalar()
#         assert value == 1
#
#
# @pytest.mark.asyncio
# async def test_dispose_engine(db_helper: DatabaseHelper) -> None:
#     # Проверяем статус пула до dispose()
#     logger.info(
#         "До dispose(): %s",
#         db_helper.engine._proxied.pool.status(),
#     )
#
#     # Закрываем пул
#     await db_helper.dispose()
#
#     # Проверяем статус пула после dispose()
#     logger.info(
#         "После dispose(): %s",
#         db_helper.engine._proxied.pool.status(),
#     )
#
#     # # Проверяем, что пул закрыт
#     # assert db_helper.engine._proxied.pool.is_closed(), "Пул не закрыт!"
#
#     # # Пытаемся получить соединение (должно вызвать ошибку)
#     # with pytest.raises(ResourceClosedError) as exc_info:
#     #     async with db_helper.engine.connect() as conn:
#     #         await conn.execute(text("SELECT 1"))
#     #
#     # assert "This Connection is closed" in str(exc_info.value),
#     # "Ожидалась ошибка закрытого соединения!"
