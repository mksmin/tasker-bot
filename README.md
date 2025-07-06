# Телеграм бот с ежедневной отправкой аффирмаций пользователя

Бот, который сохраняет позитивные аффирмации от пользователя и отправляет их рандомно каждый день в установленное
пользователем время

## Цель проекта

- Отработка навыков разработки, тестирования и развертывания  
- Разработка личного web-инструментария для решения личных задач  
- Демонстрация навыков: архитектура, ООП, Docker, CI/CD, тестирование

---

## Стек

| Компонент       | Технология              |
|-----------------|-------------------------|
| Язык            | Python 3.10             |
| Бот             | aiogram                 |
| База данных     | PostgreSQL + SQLAlchemy |
| Миграции        | Alembic                 |
| Тестирование    | pytest                  |
| CI/CD           | GitHub Actions          |
| Контейнеризация | Docker + docker-compose |
| Планировщик     | apscheduler             |

## Структура

```text
├── .dockerignore
├── .env.template           # Шаблон .env файла
├── .github                 # CI: GitHub Actions
├── .gitignore
├── Dockerfile
├── alembic.ini
├── alembic/                # Миграции БД
│
├── app/                    # Логика Telegram-бота
│   ├── handlers.py         # Обработчики команд
│   ├── keyboards.py        # Инлайн-клавиатуры
│   ├── rabbit_tasks.py     # Задачи из RabbitMQ
│   ├── scheduler.py        # Планировщик (apscheduler)
│   ├── statesuser.py       # FSM состояния
│   └── utils.py            # Дополнительные утилиты
│
├── config/
│   └── config.py           # Загрузка конфигов из .env
│
├── database/               # Работа с БД
│   ├── config.py
│   ├── crud/               # CRUD менеджеры
│   │   ├── crud_manager.py # Главный CRUDManager
│   │   └── managers/       # Менеджеры на модели
│   ├── db_helper.py        # Инициализация движка и сессий
│   ├── models.py           # Модели SQLAlchemy
│   ├── requests.py         # Старые запросы (заменяются)
│   └── schemas/            # Pydantic-схемы
│
├── tests/                  # Тесты
│
├── docker-compose.yml      
├── pyproject.toml          # Poetry зависимости
├── poetry.lock             
├── pytest.ini              # Конфиг для pytest
└── run.py                  # Точка входа: запуск бота
```

## Запуск проекта

### 1. Клонировать репозиторий

```bash
git clone https://github.com/mksmin/tasker-bot.git
cd tasker-bot
```

### 2. Настроить переменные окружения

```bash
cp .env.template .env
# затем отредактировать .env
```

### 3. Собрать и запустить контейнеры

```bash
docker-compose up --build -d bot
```

## Тестирование

```bash
docker-compose run --rm bot poetry run pytest -s
```

# CI/CD

Проект использует **GitHub Actions**:
- Прогон автотестов при каждом push в ветку `master`
- Автоматический деплой на сервер по SSH  

# Особенности
- Покрытие юнит-тестами _(53% по coverage)_  
- Асинхронный стек: `aiogram`, `async SQLAlchemy`, `async APScheduler`  
- Используется ООП _(CRUD-менеджеры, сессии и конфиг через `.env`)_
- Поддержка RabbitMQ для обработки задач от FastAPI сервера  
*Пока обязательный компонент, отключение будет доступно позже*