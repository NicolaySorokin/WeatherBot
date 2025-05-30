# Telegram бот для показа погоды

## Описание
Данный проект позволяет с помощью бота телеграм и API WeatherAPI.com получать данные о погоде. В проекте реализованы различные города. Вы также можете добавить и другие города.

## Установка

1. Клонировать репозиторий:

    ```bash
    git clone <ссылка на репозиторий>
    ```

2. Cоздать и активировать виртуальное окружение:

    ```bash
    python3 -m venv venv

    source venv/bin/activate
    ```

    Если у вас Windows, то процесс будет таким:

    ```bash
    python -m venv venv
    source venv/Scripts/activate
    ```

3. Обновить pip. Далее установить зависимости из файла requirements.txt:

    ```bash
    python3 -m pip install --upgrade pip

    pip install -r requirements.txt
    ```

    Для Windows:

    ```bash
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ```

4. Создайте .env файл на основе .env.example и вставьте туда ваш токен и API-ключ:

    ```bash
    TOKEN=<your_telegram_token>
    API_KEY=<your_api_key>
    ```

5. Запустите бота:

    ```bash
    python3 bot_weather.py
    ```

    Для Windows:

    ```bash
    python bot_weather.py
    ```


## Бот телеграм

### Как работает бот

Бот запускается с помощью команды:

    /start

Дальше появится меню с кнопками.

В главном меню будет три кнопки:

-Выбрать город (пользователь выбирает доступные города, в котором будет показываться погода)

-Показать погоду (показывает текущую погоду в выбранном городе)

-Выбрать время (выбирается время для ежедневной отправки погоды)


Если выбран город, при нажатии "Показать погоду" бот отправит в чат сообщение в примерном формате:

```bash
Прогноз погоды для Москва:
Солнечно
Температура: 26.4°C
Влажность: 28%
Ветер: 25.6 км/ч
```

Если город не выбран, то будет отправлено сообщение о просьбе выбрать город.