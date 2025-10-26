from pydantic import BaseModel


class BaseQuery(BaseModel):
    """Базовый запрос (для RPC)"""


class GetAffirmationQuery(BaseQuery):
    affirmation_id: int


class GetUserAffirmationsQuery(BaseQuery):
    user_tg: int
    count: int = 10


class GetPaginatedAffirmationsQuery(BaseQuery):
    user_tg: int
    limit: int
    offset: int


class GetUserSettingsQuery(BaseQuery):
    user_tg: int
