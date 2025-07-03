from .base import BaseCRUDManager
from database.models import User
from database.schemas import UserCreateSchema
from database import db_helper


class UserManager(BaseCRUDManager[User]):

    def __init__(self):
        super().__init__(model=User, session_maker=db_helper.session_factory)

    async def create_user(self, user_data: dict):
        instance = UserCreateSchema(**user_data)
        return await super().create(data=instance)
