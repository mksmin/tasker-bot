from .repositories import UserRepository
from .managers import UserManager


class CRUDManager:
    def __init__(self):
        self.user: UserManager = UserManager(repo=UserRepository())


crud_manager = CRUDManager()