from urllib.parse import quote

from pydantic import BaseModel
from pydantic import computed_field


class RabbitMQConfig(BaseModel):
    host: str = "host"
    port: int = 1234
    username: str
    password: str
    vhostname: str
    secure: bool = True

    @computed_field  # type: ignore[prop-decorator]
    @property
    def url(self) -> str:
        safe_username = quote(self.username, safe="")
        safe_password = quote(self.password, safe="")
        safe_vhost = quote(self.vhostname, safe="")
        domain = quote(self.host.encode("idna").decode())
        protocol = "amqps" if self.secure else "amqp"

        return f"{protocol}://{safe_username}:{safe_password}@{domain}:{self.port}/{safe_vhost}"
