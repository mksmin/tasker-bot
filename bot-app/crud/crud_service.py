from contextlib import AbstractAsyncContextManager, asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from crud.managers import UserManager
from crud.services.affirmations import AffirmationService
from crud.services.users import UserService
from database import db_helper


class CRUDService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session: AsyncSession = session
        self.user: UserService = UserService(self._session)
        self.affirm: AffirmationService = AffirmationService(
            self._session,
            UserManager(self._session),
        )


def get_crud_service(
    session: AsyncSession,
) -> CRUDService:
    return CRUDService(session)


@asynccontextmanager  # type: ignore[arg-type]
async def get_crud_service_with_session() -> AbstractAsyncContextManager[CRUDService]:  # type: ignore[misc]
    async with db_helper.session_factory() as session:
        crud = CRUDService(session)
        yield crud
