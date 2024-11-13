# Psychologist Schedule Bot

<p align="center">
   <img src="https://img.shields.io/badge/python-3.10-green" alt="Python Version">
   <img src="https://img.shields.io/badge/version-v1.0b-lightgrey" alt="Project Version">
   <img src="https://img.shields.io/badge/language-ru-blue" alt="Language">
   <br>
   <img src="https://img.shields.io/badge/aiogram-3.13.1-green" alt="aiogram Version">
   <img src="https://img.shields.io/badge/aiohttp-3.10.10-green" alt="aiohttp Version">
   <img src="https://img.shields.io/badge/beautifulsoup4-4.12.3-green" alt="BeautifulSoup Version">
   <img src="https://img.shields.io/badge/requests-2.32.3-green" alt="Requests Version">
</p>


Этот бот предназначен для мониторинга расписания консультаций у психолога Службы психологической поддержки студентов РТУ МИРЭА и уведомления о появлении новых доступных временных слотов.

## Описание

Скрипт использует `requests` и `BeautifulSoup` для получения данных с сайта, асинхронную библиотеку `aiogram` для взаимодействия с Telegram API, `logging` для ведения журнала событий. Бот автоматически проверяет расписание, обновляет JSON-файл с записями и уведомляет о новых временных слотах.

## Функционал

1. **Периодическая проверка расписания**
2. **Уведомления о новых слотах**:
3. **Обработка ошибок**

## Установка

1. Склонируйте репозиторий:
    ```bash
    git clone https://github.com/extpankov/psy-mirea
    cd psy-mirea
    ```
2. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```
3. Создайте файл `config.py` на основе `example.config.py` и добавьте следующие переменные:
    ```python
    BOT_TOKEN = "ваш токен бота"
    CHAT_ID = "ID чата для уведомлений"
    cookies = { ... }    # Cookies для запроса
    headers = { ... }    # Заголовки для запроса
    params = { ... }     # Параметры запроса
    ```
4. Запустите бота:
    ```bash
    python bot.py
    ```
    
## Логика работы

1. **Метод `check_schedule`**: Проверяет расписание на 10 ближайших дней.
2. **Метод `notify_changes`**: Отправляет уведомления в случае появления новых слотов.
3. **Метод `periodic_check`**: Выполняет проверку каждые 15 минут.

