from typing import AsyncGenerator, Any
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
    AsyncSession,
)
from config import settings


class DatabaseHelper:
    def __init__(
        self,
        url: str,
        echo: bool = False,  # noqa: FBT002, FBT001
        echo_pool: bool = False,  # noqa: FBT002, FBT001
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> None:
        self.url = url
        self._init_engine(echo, echo_pool, pool_size, max_overflow)

    def _init_engine(
        self,
        echo: bool,  # noqa: FBT001
        echo_pool: bool,  # noqa: FBT001
        pool_size: int,
        max_overflow: int,
    ) -> None:
        url_obj = make_url(self.url)
        kwargs: dict[str, Any] = {
            "echo": echo,
            "echo_pool": echo_pool,
        }

        if url_obj.drivername != "sqlite+aiosqlite" or url_obj.database != ":memory:":
            kwargs.update({"pool_size": pool_size, "max_overflow": max_overflow})

        self.engine: AsyncEngine = create_async_engine(self.url, **kwargs)
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        await self.engine.dispose()

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session


db_helper = DatabaseHelper(
    url=str(settings.db.url),
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
)
