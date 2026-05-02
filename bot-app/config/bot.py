from pydantic import BaseModel


class BotConfig(BaseModel):
    token: str
    owner_tg_id: int
    proxy_url: str | None = None
