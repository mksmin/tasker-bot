from .managers import UserManager, TaskManager
from database import db_helper


class CRUDManager:
    def __init__(self) -> None:
        self.user: UserManager = UserManager(session_maker=db_helper.session_factory)
        self.task: TaskManager = TaskManager(session_maker=db_helper.session_factory)

        self.task.set_user_manager(self.user)


crud_manager = CRUDManager()
