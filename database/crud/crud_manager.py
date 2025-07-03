from .managers import UserManager


class CRUDManager:
    def __init__(self):
        self.user: UserManager = UserManager()


crud_manager = CRUDManager()
