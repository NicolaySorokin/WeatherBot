import os

import pytz
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

load_dotenv()

TOKEN = os.getenv('TOKEN')
WEATHER_API_KEY = os.getenv('API_KEY')

city_mapping = {
    "Москва": "Moscow",
    "Санкт-Петербург": "Saint Petersburg",
    "Новосибирск": "Novosibirsk",
    "Екатеринбург": "Yekaterinburg",
    "Лондон": "London",
    "Нью-Йорк": "New York"
}
cities = list(city_mapping.keys())

scheduler = BackgroundScheduler(timezone=pytz.timezone('Europe/Moscow'))
scheduler.start()

CITY, TIME = 1, 2
main_keyboard = [['Выбрать город', 'Выбрать время'], ['Показать погоду']]
main_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)


def start(update, context):
    update.message.reply_text("Привет, я бот погоды", reply_markup=main_markup)


def choose_city(update, context):
    keyboard = [[city] for city in cities]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text("Выберите город:", reply_markup=reply_markup)
    return CITY


def city_choice(update, context):
    city = update.message.text
    if city in city_mapping:
        context.user_data['city'] = city
        context.user_data['city_query'] = city_mapping[city]
        update.message.reply_text(f"Город выбран: {city}", reply_markup=main_markup)
        if 'time' in context.user_data:
            schedule_daily_weather(update, context)
    else:
        update.message.reply_text("Выберите город из списка", reply_markup=main_markup)
    return ConversationHandler.END


def set_time(update, context):
    update.message.reply_text("Введите время отправки прогноза погоды в формате ЧЧ:ММ", reply_markup=ReplyKeyboardRemove())
    return TIME


def time_choice(update, context):
    time_str = update.message.text
    try:
        hour, minute = map(int, time_str.split(':'))
        if 0 <= hour < 24 and 0 <= minute < 60:
            context.user_data['time'] = time_str
            update.message.reply_text(f"Время отправки выбрано: {time_str}", reply_markup=main_markup)
            if 'city' in context.user_data:
                schedule_daily_weather(update, context)
        else:
            update.message.reply_text("Неверный формат времени. Попробуйте еще раз", reply_markup=main_markup)
    except:
        update.message.reply_text("Неверный формат времени. Попробуйте еще раз", reply_markup=main_markup)
    return ConversationHandler.END


def schedule_daily_weather(update, context):
    chat_id = update.effective_chat.id
    city_query = context.user_data['city_query']
    city_name = context.user_data['city']
    time_str = context.user_data['time']
    hour, minute = map(int, time_str.split(':'))
    job_id = str(chat_id)
    scheduler.add_job(send_weather, 'cron', args=[chat_id, city_query, city_name], hour=hour, minute=minute, id=job_id, replace_existing=True)
    context.bot.send_message(chat_id=chat_id, text=f"Настроен ежедневный прогноз погоды на {time_str}. Город {city_name}")


def show_weather(update, context):
    chat_id = update.effective_chat.id
    if 'city' in context.user_data:
        city_query = context.user_data['city_query']
        city_name = context.user_data['city']
        res = requests.get(f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city_query}&lang=ru")
        data = res.json()
        temp = data['current']['temp_c']
        cond = data['current']['condition']['text']
        humidity = data['current']['humidity']
        wind = data['current']['wind_kph']
        text = f"Погода в {city_name}: {cond}\nТемпература: {temp}°C\nВлажность: {humidity}%\nВетер: {wind} км/ч"
        context.bot.send_message(chat_id=chat_id, text=text)
    else:
        context.bot.send_message(chat_id=chat_id, text="Сначала выберите город.")
    context.bot.send_message(chat_id=chat_id, text="Выберите действие:", reply_markup=main_markup)


def send_weather(chat_id, city_query, city_name):
    res = requests.get(f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city_query}&lang=ru")
    data = res.json()
    temp = data['current']['temp_c']
    cond = data['current']['condition']['text']
    humidity = data['current']['humidity']
    wind = data['current']['wind_kph']
    text = f"Прогноз погоды для {city_name}:\n{cond}\nТемпература: {temp}°C\nВлажность: {humidity}%\nВетер: {wind} км/ч"
    bot.send_message(chat_id=chat_id, text=text)


def main():
    updater = Updater(TOKEN, use_context=True)
    global bot
    bot = updater.bot
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^Выбрать город$'), choose_city),
                      MessageHandler(Filters.regex('^Выбрать время$'), set_time)],
        states={
            CITY: [MessageHandler(Filters.text & ~Filters.command, city_choice)],
            TIME: [MessageHandler(Filters.text & ~Filters.command, time_choice)]
        },
        fallbacks=[]
    )
    dp.add_handler(conv_handler)
    dp.add_handler(MessageHandler(Filters.regex('^Показать погоду$'), show_weather))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
