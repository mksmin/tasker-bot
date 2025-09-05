FROM python:3.10-slim
LABEL authors="mks_min"

# Установка poetry
ENV POETRY_VERSION=2.1.1
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /taskerbot

# Установка зависимостей
COPY pyproject.toml poetry.lock ./
RUN poetry config  virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi --with main,tests

# Копирование исходного кода приложения
COPY . .

# Команда для запуска приложения
CMD ["python", "-u", "bot-app/run.py"]