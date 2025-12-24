# import lib
import logging
from pathlib import Path
from urllib.parse import quote

from pydantic import BaseModel, HttpUrl, PostgresDsn, ValidationError, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
PROJECT_DIR = Path(__file__).resolve().parent.parent


class BotConfig(BaseModel):
    token: str
    owner_tg_id: int


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
                scheme=f"{self.scheme}+{self.engine}",
                username=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
                path=self.path,
            )
        except ValidationError:
            logger.exception("Invalid connection string")
            raise
        return PostgresDsn(url_path)


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

    webhook: WebhookConfig


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            PROJECT_DIR / ".env.template",
            PROJECT_DIR / ".env",
        ),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        yaml_file=(
            PROJECT_DIR / "config.default.yaml",
            PROJECT_DIR / "config.local.yaml",
        ),
        yaml_config_section="tasks-bot",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Define the sources and their order for loading the settings values.

        Args:
            settings_cls: The Settings class.
            init_settings: The `InitSettingsSource` instance.
            env_settings: The `EnvSettingsSource` instance.
            dotenv_settings: The `DotEnvSettingsSource` instance.
            file_secret_settings: The `SecretsSettingsSource` instance.

        Returns:
            A tuple containing the sources and their order
            for loading the settings values.
        """
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            YamlConfigSettingsSource(settings_cls),
        )

    bot: BotConfig
    db: DatabaseConfig
    rabbit: RabbitMQConfig
    run: RunConfig


settings = Settings()
