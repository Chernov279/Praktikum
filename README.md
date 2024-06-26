# Praktikum 2024

Этот проект представляет собой веб-приложение, парсящее вакансии из сайта hh.ru при помощи библиотеки selenium, и Telegram-бота для отображения в удобном формате.

## Требования

- Docker
- Docker Compose

## Установка и запуск

Следуйте этим шагам, чтобы установить и запустить проект на вашем компьютере.

### 1. Клонирование репозитория

Сначала клонируйте репозиторий проекта:

```sh
git clone https://github.com/Chernov279/Praktikum.git cd yourproject
```
### 2. Настройка переменных окружения
Создайте файл .env в корне проекта и добавьте туда ваши Telegram токен и параметры базы данных:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost/prak
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=prak
POSTGRES_HOST=db
POSTGRES_PORT=5432
TELEGRAM_BOT_TOKEN=your_telegram_token
```
### 3. Сборка Docker-образа
Соберите Docker-образ проекта с помощью Docker Compose:

```sh
docker-compose build
```
### 4. Запуск контейнеров
Запустите Docker-контейнеры:

```sh
docker-compose up
```
### 5. Проверка работы
После запуска контейнеров:

Откройте браузер и перейдите по адресу http://localhost:8000, чтобы проверить работу веб-приложения.
Проверьте работу вашего Telegram-бота, отправив команду или сообщение в ваш бот.
### 6. Остановка контейнеров
Для остановки контейнеров нажмите Ctrl+C в терминале, где запущена команда docker-compose up, или выполните команду:

```sh
docker-compose down
```

### 7. Используемые технологии и инструменты
Проект был реализован с использованием следующих технологий и инструментов:

 - Python
 - FastAPI
 - Selenium
 - beatiful soup 4
 - chromedriver_py: Пакет для автоматической установки драйвера Chrome (необходим для корректной работы selenium).
 - SQLAlchemy
 - PostgreSQL
 - forex_python: Библиотека для конвертирования валюты.
### 8. Структура проекта
Dockerfile - конфигурационный файл для создания Docker-образа.
docker-compose.yml - файл для настройки и запуска контейнеров.
requirements.txt - файл зависимостей проекта.
app/main.py - основной файл веб-приложения.
app/telegram.py - файл для работы с Telegram-ботом.