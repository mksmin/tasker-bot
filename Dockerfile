FROM python:3.10-slim
WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода приложения
COPY . .

# Команда для запуска приложения
CMD ["python", "-u", "run.py"]