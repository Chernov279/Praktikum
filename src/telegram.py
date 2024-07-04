import telebot
from telebot import types
import requests

TOKEN = '7499761737:AAEO706uu3_XVOAk4gMTFSVeMONoxEBpQIc'
bot = telebot.TeleBot(TOKEN)

user_data = {}

start_message = "Привет! Давайте найдем вакансии, которые вас интересуют"

dictionary = {
    "Полная занятость": "full",
    "Частичная занятость ": "part",
    "Проектная работа ": "project",
    "Волонтерство": "volunteer",
    "Стажировка": "probation",
    "Не указывать": None,
    "Полный день": "fullDay",
    "Сменный график": "shift",
    "Гибкий график": "flexible",
    "Удаленная работа": "remote",
    "Вахтовый метод": "flyInFlyOut",
    "Без опыта": "noExperience",
    "От 1 до 3 лет": "between1And3",
    "От 3 до 6 лет": "between3And6",
    "Более 6 лет": "moreThan6",
    "Не имеет значения": "doesNotMatter",
    "Проектная работа": "employment_project",
    "Частичная занятость": "employment_part",
    "От четырех до шести часов в день": "from_four_to_six_hours_in_a_day",
    "Только суббота и воскресенье": "only_saturday_and_sunday",
    "Начало после 16:00": "start_after_sixteen",
    "Показать еще": True,
    "Выйти в главное меню": False
}


def generate_markup(options):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for option in options:
        markup.add(types.KeyboardButton(option))
    return markup


@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, start_message)
    user_data[message.chat.id] = {'state': 'WAITING_FOR_START'}
    bot.send_message(message.chat.id, 'Выберите, что вы хотите сделать', reply_markup=generate_markup([
        'Просмотреть вакансии на сайте', 'Провести аналитику с уже имеющимися данными в базе данных']))


@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('state') == 'WAITING_FOR_START')
def handle_profession(message):
    if message.text == 'Просмотреть вакансии на сайте':
        user_data[message.chat.id]['state'] = 'WAITING_FOR_MAIN'
        bot.send_message(message.chat.id, 'Напишите, какая вакансия вам интересна')
    elif message.text == 'Провести аналитику с уже имеющимися данными в базе данных':
        user_data[message.chat.id]['state'] = 'WAITING_FOR_ANALYTICS'
        bot.send_message(message.chat.id, 'Выберите логику аналитики', reply_markup=generate_markup([
            "Аналитика по названию вакансии", "Аналитика по названию компании"
        ]))
    else:
        bot.send_message(message.chat.id, 'Выберите из предложенных в списке')


@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('state') == 'WAITING_FOR_ANALYTICS')
def get_analytics(message):
    if message.text == "Аналитика по названию вакансии":
        user_data[message.chat.id]['state'] = 'WAITING_FOR_TITLE_ANALYTICS'
        bot.send_message(message.chat.id, "Напишите, какая вакансия вам интересна")
    elif message.text == "Аналитика по названию компании":
        user_data[message.chat.id]['state'] = 'WAITING_FOR_COMPANY_ANALYTICS'
        bot.send_message(message.chat.id, "Напишите, какая компания вам интересна. Убедитесь, что вы правильно написали ее название")
    else:
        bot.send_message(message.chat.id, 'Выберите из предложенных в списке')


def send_data_to_endpoint_analytics_title(chat_id, title):
    url = f"http://127.0.0.1:8000/analytics/title?title={title}"
    headers = {'Content-Type': 'application/json'}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        bot.send_message(chat_id, f"Произошла какая-то ошибка")


@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('state') == 'WAITING_FOR_TITLE_ANALYTICS')
def get_title_analytics(message):
    # response = send_data_to_endpoint_analytics_title(message.chat.id, message.text)
    bot.send_message(message.chat.id, send_data_to_endpoint_analytics_title(message.chat.id, message.text))
    user_data[message.chat.id]['state'] = 'WAITING_FOR_START'
    bot.send_message(message.chat.id, "Учтите, что информация может быть неточной или неверной",
                     reply_markup=generate_markup(["Вернуться в главное меню"]))


@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('state') == 'WAITING_FOR_MAIN')
def get_vacancy(message):
    user_data[message.chat.id]['vacancy'] = message.text if message.text else None
    user_data[message.chat.id]['state'] = 'WAITING_FOR_EXPERIENCE'
    bot.send_message(message.chat.id, 'Выберите опыт работы:', reply_markup=generate_markup([
        'Без опыта', 'От 1 до 3 лет', 'От 3 до 6 лет', 'Более 6 лет', 'Не имеет значения'
    ]))


@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('state') == 'WAITING_FOR_EXPERIENCE')
def get_experience(message):
    user_data[message.chat.id]['experience'] = dictionary[message.text] if message.text else None
    user_data[message.chat.id]['state'] = 'WAITING_FOR_EMPLOYMENT'
    bot.send_message(message.chat.id, 'Выберите тип занятости:', reply_markup=generate_markup([
        'Полная занятость', 'Частичная занятость', 'Проектная работа', 'Волонтерство', 'Стажировка', 'Не указывать'
    ]))


@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('state') == 'WAITING_FOR_EMPLOYMENT')
def get_employment(message):
    user_data[message.chat.id]['employment'] = dictionary[message.text] if message.text else None
    user_data[message.chat.id]['state'] = 'WAITING_FOR_SCHEDULES'
    bot.send_message(message.chat.id, 'Выберите тип графика:', reply_markup=generate_markup([
        'Полный день', 'Сменный график', 'Гибкий график', 'Удаленная работа', 'Вахтовый метод', 'Не указывать'
    ]))


@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('state') == 'WAITING_FOR_SCHEDULES')
def get_schedule(message):
    user_data[message.chat.id]['schedule'] = dictionary[message.text] if message.text else None
    user_data[message.chat.id]['state'] = 'WAITING_FOR_PART_TIMES'
    bot.send_message(message.chat.id, 'Выберите параметры неполного рабочего дня:', reply_markup=generate_markup([
        'Проектная работа', 'Частичная занятость', 'От четырех до шести часов в день', 'Только суббота и воскресенье', 'Начало после 16:00', 'Не указывать'
    ]))


@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('state') == 'WAITING_FOR_PART_TIMES')
def get_part_times(message):
    user_data[message.chat.id]['part_times'] = dictionary[message.text] if message.text else None
    user_data[message.chat.id]['state'] = 'WAITING_FOR_SALARY'
    bot.send_message(message.chat.id, 'Введите зарплату, не меньше которой вы хотите получать:')


@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('state') == 'WAITING_FOR_SALARY')
def get_salary(message):
    try:
        user_data[message.chat.id]['salary'] = int(message.text)
        user_data[message.chat.id]['state'] = 'WAITING_FOR_PARSER'
        user_data[message.chat.id]['page_num'] = 0
        send_data_to_endpoint_vacancies(message.chat.id)
        bot.send_message(message.chat.id, "Хотите посмотреть еще или хотите выйти в главное меню?", reply_markup=generate_markup([
                'Показать еще', 'Выйти в главное меню'
            ]))
    except ValueError:
        bot.send_message(message.chat.id, "Введите число")


@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('state') == 'WAITING_FOR_PARSER')
def handle_parser(message):
    if message.text == "Показать еще":
        user_data[message.chat.id]['page_num'] += 1
        send_data_to_endpoint_vacancies(message.chat.id)
        bot.send_message(message.chat.id, "Хотите посмотреть еще или хотите выйти в главное меню?", reply_markup=generate_markup([
                'Показать еще', 'Выйти в главное меню'
            ]))
    else:
        user_data[message.chat.id]['state'] = 'WAITING_FOR_START'
        bot.send_message(message.chat.id, "Напишите, что вы хотите сделать")


def send_data_to_endpoint_vacancies(chat_id):
    url = 'http://127.0.0.1:8000/vacancies'
    headers = {'Content-Type': 'application/json'}
    payload = {
        'keyword': user_data[chat_id].get('vacancy'),
        'page': str(user_data[chat_id].get('page_num')),
        'experience': user_data[chat_id].get('experience'),
        'employment': user_data[chat_id].get('employment'),
        'schedule': user_data[chat_id].get('schedule'),
        'part_time': user_data[chat_id].get('part_times'),
        'salary': str(user_data[chat_id].get('salary'))
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        vacancies = response.json().get("vacancies", [])
        if vacancies:
            for vacancy in vacancies:
                bot.send_message(chat_id, format_vacancy(vacancy))
            bot.send_message(chat_id, "Вот вакансии, которые были найдены")
        else:
            bot.send_message(chat_id, "На такой запрос не было найдено вакансий")
    else:
        bot.send_message(chat_id, f"Произошла ошибка при отправке вашего запроса.")


def format_vacancy(vacancy):
    return (
        f"Название: {vacancy['title']}\n"
        f"Опыт: {vacancy.get('experience', 'Не указано')}\n"
        f"Компания: {vacancy.get('company', 'Не указано')}\n"
        f"Зарплата: {vacancy.get('salary', 'Не указано')}\n"
        f"Локация: {vacancy.get('location', 'Не указано')}\n"
        f"Ссылка: {vacancy.get('link', 'Не указано')}"
    )


bot.polling(none_stop=True)