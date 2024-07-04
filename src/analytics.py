from collections import Counter
import re
from typing import Union

from src.database import Vacancy
from forex_python.converter import CurrencyCodes
import requests
from bs4 import BeautifulSoup


def get_currency_rate_parser(currency_code):
    url = f"https://cbr.ru/currency_base/daily/"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Находим таблицу с данными по валютам
        table = soup.find('table', class_='data')

        # Поиск строк таблицы
        rows = table.find_all('tr')

        for row in rows:
            # Извлекаем значения из каждой строки
            cols = row.find_all('td')
            if len(cols) >= 2:
                currency = cols[1].text.strip()
                rate_rub = cols[-1].text.strip().replace(",", ".")
                rate_currency = cols[2].text.strip().replace(",", ".")

                # Проверяем, соответствует ли код валюты искомому
                if currency == currency_code:
                    return round(float(rate_rub) / float(rate_currency), 2)


def get_currency_rate(amount: Union[str, float] = 1, symbol: str = '₽'):
    try:
        amount = float(amount)
    except:
        return
    code = CurrencyCodes()
    if symbol == '₽' and amount:
        return amount
    elif symbol == '$':
        currency_code = "USD"
    elif symbol == '₸':
        currency_code = "KZT"
    else:
        currency_code = code.get_currency_code_from_symbol(symbol)

    if currency_code:
        currency_rate = get_currency_rate_parser(currency_code)
        if currency_rate and amount:
            return round(float(currency_rate) * amount, 2)


def extract_salary(salary_str):
    salary_str = salary_str.replace(" ", "").replace(" ", "")
    salary_numbers = re.findall(r'\d+.', salary_str)
    if len(salary_numbers) == 1:
        return get_currency_rate(salary_numbers[0][:-1], salary_numbers[0][-1])
    elif len(salary_numbers) == 2:
        try:
            salary_amount = (float(salary_numbers[0][:-1]) + float(salary_numbers[-1][:-1])) // 2
            return get_currency_rate(salary_amount, salary_numbers[-1][-1])
        except:
            return


def format_analytics_by_title(result):
    locations = result.get('location_distribution', {})
    loc_pers = [f"{location}: {percent}%" for location, percent in locations.items()]
    companies = result.get('company_distribution', {})
    com_pers = [f"{company}: {percent}%" for company, percent in companies.items()]

    experience_distribution = result.get('experience_distribution', {})

    return (
        f"Всего вакансий найдено: {result['total_vacancies']}\n"
        f"Средний требуемый опыт: {result.get('average_experience', 'Недостаточно данных')} лет, среди которых в процентном соотношении:\n"
        f"  - Без опыта: {experience_distribution.get('Без опыта', 'Недостаточно данных')}%\n"
        f"  - Опыт 1-3 года: {experience_distribution.get('Опыт 1-3 года', 'Недостаточно данных')}%\n"
        f"  - Опыт 3-6 лет: {experience_distribution.get('Опыт 3-6 лет', 'Недостаточно данных')}%\n"
        f"  - Опыт более 6 лет: {experience_distribution.get('Опыт более 6 лет', 'Недостаточно данных')}%\n"
        f"Средняя зарплата: {result.get('average_salary', 'Недостаточно данных')} руб.\n"
        f"Процентиль вакансий по локациям:\n"
        f"{''.join(loc_pers)}\n"
        f"Процентиль вакансий по компаниям:\n"
        f"{''.join(com_pers)}\n"
    )


def analytics_by_title(title: str, session):
    python_vacancies = session.query(Vacancy).filter(Vacancy.title.ilike(f'%{title}%')).all()
    experience_counter = Counter(vacancy.experience for vacancy in python_vacancies)
    total_vacancies = len(python_vacancies)

    experience_mapping = {
        'Без опыта': 0,
        'Опыт 1-3 года': 2,
        'Опыт 3-6 лет': 4.5,
        'Опыт более 6 лет': 7
    }
    experience_years = [experience_mapping.get(vacancy.experience, 0) for vacancy in python_vacancies]
    average_experience = sum(experience_years) / len(experience_years) if experience_years else 0

    salaries = [extract_salary(vacancy.salary) for vacancy in python_vacancies if vacancy.salary and extract_salary(vacancy.salary) is not None]
    average_salary = sum(salaries) / len(salaries) if salaries else 0

    location_counter = Counter(vacancy.location for vacancy in python_vacancies)

    company_counter = Counter(vacancy.company for vacancy in python_vacancies)

    result = {
        "total_vacancies": total_vacancies,
        "average_experience": round(average_experience, 2),
        "experience_distribution": {experience: round((count / total_vacancies) * 100, 2) for experience, count in experience_counter.items() if (count / total_vacancies) * 100 > 3},
        "average_salary": round(average_salary, 2),
        "location_distribution": {location: round((count / total_vacancies) * 100, 2) for location, count in location_counter.items() if (count / total_vacancies) * 100 > 3},
        "company_distribution": {company: round((count / total_vacancies) * 100, 2) for company, count in company_counter.items() if (count / total_vacancies) * 100 > 1}
    }
    return format_analytics_by_title(result)
