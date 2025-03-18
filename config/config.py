# import lib
import logging
import os

from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel, PostgresDsn, ValidationError
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)

logger = logging.getLogger(__name__)


def get_token(name_of_token: str) -> str | None:
    path_env = Path(__file__).parent.absolute() / '.env'

    if path_env.exists():
        load_dotenv(path_env)
        return os.getenv(name_of_token)

    return None


class BotConfig(BaseModel):
    token: str


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__"
    )
    bot: BotConfig
    db: DatabaseConfig


settings = Settings()
