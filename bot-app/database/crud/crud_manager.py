from database import db_helper

from .managers import TaskManager, UserManager


class CRUDManager:
    def __init__(self) -> None:
        self.user: UserManager = UserManager(session_maker=db_helper.session_factory)
        self.task: TaskManager = TaskManager(session_maker=db_helper.session_factory)

        self.task.set_user_manager(self.user)


crud_manager = CRUDManager()
