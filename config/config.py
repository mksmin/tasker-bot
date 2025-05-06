# import lib
import logging
import os
from urllib.parse import quote

from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel, PostgresDsn, ValidationError, computed_field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)
from pydantic_core import MultiHostUrl

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_token(name_of_token: str) -> str | None:
    path_env = Path(__file__).parent.absolute() / '.env'

    if path_env.exists():
        load_dotenv(path_env)
        return os.getenv(name_of_token)

    return None


class BotConfig(BaseModel):
    token: str


class DatabaseConfig(BaseModel):
    scheme: str
    engine: str = "asyncpg"
    username: str
    password: str
    host: str = "localhost"
    port: int = 5432
    path: str = "postgres"

    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    @property
    def url(self) -> PostgresDsn:
        try:
            url_path = MultiHostUrl.build(
                scheme=f'{self.scheme}+{self.engine}',
                username=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
                path=self.path,
            )
        except ValidationError as err:
            logger.error(f"Invalid connection string for {self.name}: {err}")
            raise err
        return PostgresDsn(url_path)


class RabbitMQConfig(BaseModel):
    host: str = "localhost"
    port: int = 5672
    username: str = "user"
    password: str = "wpwd"
    vhostname: str = "vhost"

    @computed_field
    @property
    def url(self) -> str:
        safe_username = quote(self.username, safe="")
        safe_password = quote(self.password, safe="")
        safe_vhost = quote(self.vhostname, safe="")
        domain = quote(self.host.encode("idna").decode())

        return f"amqps://{safe_username}:{safe_password}@{domain}:{self.port}/{safe_vhost}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__"
    )
    bot: BotConfig
    db: DatabaseConfig
    rabbit: RabbitMQConfig = RabbitMQConfig()


settings = Settings()
