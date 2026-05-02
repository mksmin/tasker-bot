from typing import Final
from typing import Literal

from pydantic import BaseModel
from pydantic import HttpUrl

POLLING_MODE: Final = "polling"
WEBHOOK_MODE: Final = "webhooks"


class WebhookConfig(BaseModel):
    host: HttpUrl
    path: str

    @property
    def url(self) -> str:
        host = str(self.host).rstrip("/")
        path = self.path if self.path.startswith("/") else f"/{self.path}"
        return host + path


class RunConfig(BaseModel):
    host: str
    port: int
    mode: Literal["polling", "webhooks"] | None = POLLING_MODE

    webhook: WebhookConfig
