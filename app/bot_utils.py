from telebot import types

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

experiences = ["doesNotMatter", "noExperience", "between1And3", "between3And6", "moreThan6"]
employment = ["full", "part", "project", "volunteer", "probation"]
schedules = ["fullDay", "shift", "flexible", "remote", "flyInFlyOut"]
part_times = ["employment_project", "employment_part", "from_four_to_six_hours_in_a_day", "only_saturday_and_sunday", "start_after_sixteen"]


def generate_markup(options):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for option in options:
        markup.add(types.KeyboardButton(option))
    return markup


def format_vacancy(vacancy):
    return (
        f"Название: {vacancy['title']}\n"
        f"Опыт: {vacancy.get('experience', 'Не указано')}\n"
        f"Компания: {vacancy.get('company', 'Не указано')}\n"
        f"Зарплата: {vacancy.get('salary', 'Не указано')}\n"
        f"Локация: {vacancy.get('location', 'Не указано')}\n"
        f"Ссылка: {vacancy.get('link', 'Не указано')}"
    )