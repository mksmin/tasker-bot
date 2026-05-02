from pydantic import BaseModel
from pydantic import SecretStr
from sqlalchemy import URL


class DatabaseConfig(BaseModel):
    scheme: str = "postgresql"
    engine: str = "asyncpg"
    username: str
    password: SecretStr
    host: str = "localhost"
    port: int = 5432
    path: str = "postgres"

    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    @property
    def db_url(self) -> URL:
        return URL.create(
            drivername=f"{self.scheme}+{self.engine}",
            database=self.path,
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password.get_secret_value(),
        )
