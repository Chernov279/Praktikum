from collections import Counter
import re

from app.converter import CurrencyConverter
from app.database import Vacancy


def extract_salary(salary_str):
    salary_str = salary_str.replace(" ", "").replace(" ", "")
    salary_numbers = re.findall(r'\d+.', salary_str)
    if len(salary_numbers) == 1:
        return CurrencyConverter.get_currency_rate(salary_numbers[0][:-1], salary_numbers[0][-1])
    elif len(salary_numbers) == 2:
        try:
            salary_amount = (float(salary_numbers[0][:-1]) + float(salary_numbers[-1][:-1])) // 2
            return CurrencyConverter.get_currency_rate(salary_amount, salary_numbers[-1][-1])
        except:
            return


def format_analytics(result):
    locations = result.get('location_distribution', {})
    loc_pers = [f"{location}: {percent}%" for location, percent in sorted(locations.items(), key=lambda x: x[-1], reverse=True)]
    companies = result.get('company_distribution', {})
    com_pers = [f"{company}: {percent}%" for company, percent in sorted(companies.items(), key=lambda x: x[-1], reverse=True)]

    experience_distribution = result.get('experience_distribution', {})

    return (
        f"Всего вакансий найдено: {result['total_vacancies']}",
        f"Средний требуемый опыт: {result.get('average_experience', 'Недостаточно данных')} лет, среди которых в процентном соотношении:",
        f"  - Без опыта: {experience_distribution.get('Без опыта', '0')}%",
        f"  - Опыт 1-3 года: {experience_distribution.get('Опыт 1-3 года', '0')}%",
        f"  - Опыт 3-6 лет: {experience_distribution.get('Опыт 3-6 лет', '0')}%",
        f"  - Опыт более 6 лет: {experience_distribution.get('Опыт более 6 лет', '0')}%",
        f"Средняя зарплата: {result.get('average_salary', 'Недостаточно данных')} руб.",
        f"Процентиль вакансий по локациям:",
        '\n'.join(loc_pers) if loc_pers else "Недостаточно данных",
        f"Процентиль вакансий по компаниям:",
        '\n'.join(com_pers) if com_pers else "Недостаточно данных"
    )

def analytics(vacancies):
    """Возвращает аналитику по переданному списку вакансий"""
    total_vacancies = len(vacancies)
    experience_mapping = {'Без опыта': 0, 'Опыт 1-3 года': 2, 'Опыт 3-6 лет': 4.5, 'Опыт более 6 лет': 7}
    experience_years = [experience_mapping.get(v.experience, 0) for v in vacancies]
    average_experience = round(sum(experience_years) / len(experience_years), 2) if experience_years else 0
    salaries = [extract_salary(v.salary) for v in vacancies if v.salary and extract_salary(v.salary) is not None]
    average_salary = round(sum(salaries) / len(salaries), 2) if salaries else 0
    counter = lambda key: {k: round((v / total_vacancies) * 100, 2) for k, v in Counter(getattr(v, key) for v in vacancies).items() if (v / total_vacancies) * 100 > 3}
    result = {
        "total_vacancies": total_vacancies,
        "average_experience": average_experience,
        "experience_distribution": counter('experience'),
        "average_salary": average_salary,
        "location_distribution": counter('location'),
        "company_distribution": counter('company')
    }
    return {"result": format_analytics(result)}


def analytics_by_title(title: str, session):
    vacancies = session.query(Vacancy).filter(Vacancy.title.ilike(f'%{title}%')).all()
    return analytics(vacancies)


def analytics_by_company(company, session):
    vacancies = session.query(Vacancy).filter(Vacancy.company.ilike(f'%{company}%')).all()
    return analytics(vacancies)
