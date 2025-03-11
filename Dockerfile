# Используем официальный образ Python как базовый
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы с требованиями
COPY requirements.txt .

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    chromium-driver \
    chromium \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта в контейнер
COPY Praktikum .

# Указываем команду для запуска приложения и Telegram-бота
CMD ["sh", "-c", "uvicorn app.routers:app --host 0.0.0.0 --port 8000 & python app/main.py"]
