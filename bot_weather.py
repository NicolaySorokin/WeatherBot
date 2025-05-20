import logging
import os

import requests
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TOKEN')
WEATHER_API_KEY = os.getenv('API_KEY')

CITIES = {
    "Москва": "Moscow",
    "Казань": "Kazan"
}

user_city = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
    )


def get_weather(city: str) -> str:
    url = (
           "http://api.weatherapi.com/v1/current.json?"
           f"key={WEATHER_API_KEY}&q={city}&lang=ru"
        )
    response = requests.get(url)

    if response.status_code != 200:
        return "Ошибка при получении погоды"

    data = response.json()
    temp = data['current']['temp_c']
    pressure_mb = data['current']['pressure_mb']
    pressure_mmHg = round(pressure_mb * 0.75006)
    condition = data['current']['condition']['text']

    return f"Город: {data['location']['name']}\n" \
           f"Погода: {condition}\n" \
           f"Температура: {temp}°C\n" \
           f"Давление: {pressure_mmHg} мм рт. ст."


def start(update: Update, context: CallbackContext) -> None:
    show_main_menu(update)


def show_main_menu(update: Update):
    keyboard = [["Выбрать город", "Показать погоду"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("Главное меню:", reply_markup=reply_markup)


def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    user_id = update.message.from_user.id

    if text == "Выбрать город":
        keyboard = [["Москва", "Казань"], ["Назад"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("Выберите город:", reply_markup=reply_markup)

    elif text in CITIES:
        user_city[user_id] = text
        update.message.reply_text(f"Выбран город: {text}")

    elif text == "Показать погоду":
        city = user_city.get(user_id)
        if not city:
            update.message.reply_text("Сначала выберите город")
        else:
            weather_info = get_weather(CITIES[city])
            update.message.reply_text(weather_info)

    elif text == "Назад":
        show_main_menu(update)

    else:
        update.message.reply_text("Пожалуйста, используйте кнопки меню")


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command,
                                  handle_message))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
