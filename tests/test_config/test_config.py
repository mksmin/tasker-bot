import os
import pytest

from dotenv import load_dotenv
from config.config import BotConfig, DatabaseConfig, RabbitMQConfig, Settings, get_token
from pathlib import Path
from pydantic import PostgresDsn, ValidationError
from unittest.mock import patch


@pytest.fixture
def test_env_path():
    path = Path(__file__).parent.parent.parent / '.env.template'
    return path


@pytest.fixture
def settings(monkeypatch, test_env_path):
    # 1. Очищаем все переменные окружения
    for key in list(os.environ):
        if key.startswith("APP_CONFIG__"):
            monkeypatch.delenv(key)

    monkeypatch.setattr(
        "config.config.Path",
        lambda *args: test_env_path
    )
    try:
        return Settings(_env_file=test_env_path)
    except ValueError as e:
        pytest.fail(f'Ошибка при загрузке настроек: {e}')


@pytest.fixture
def monkeypatch_env(monkeypatch, test_env_path):

    # Подменяем путь, который используется внутри get_token, на путь к .env.test
    def mock_get_token_path(*args):
        # Печатаем подмененный путь для отладки
        return test_env_path

    # Подменяем Path, чтобы при вызове Path() возвращался путь к .env.test
    monkeypatch.setattr(
        "pathlib.Path.__truediv__", mock_get_token_path
    )
    yield


def test_get_token(monkeypatch_env):
    """Тест функции get_token"""
    token = get_token('APP_CONFIG__BOT__TOKEN')
    assert token == 'test_bot_token', 'Токен не найден или не соответствует ожидаемому'


def test_bot_config(settings):
    """Тест класса BotConfig"""
    bot_config = settings.bot

    assert isinstance(bot_config, BotConfig), 'Не является экземпляром BotConfig'
    assert isinstance(bot_config.token, str), f'Токен не является строкой'
    assert len(bot_config.token) > 0, 'Токен не должен быть пустым'
    assert bot_config.token == 'test_bot_token', (
        f'Ожидается test_bot_token, получено {bot_config.token}'
    )


def test_database_config(settings):
    db_config = settings.db

    assert isinstance(db_config, DatabaseConfig), 'Не является экземпляром DatabaseConfig'
    assert isinstance(db_config.url, PostgresDsn), 'URL не является строкой'
    assert str(db_config.url) == 'postgresql+asyncpg://user:pwd@host:1234/dbname', \
        'URL не соответствует ожидаемому'
    assert db_config.echo is False, 'echo не False'


def test_validation_error():
    """Проверяет обработку ошибок валидации"""
    with pytest.raises(ValidationError):
        BotConfig(token=None)
        DatabaseConfig(url="invalid-url")
