from selenium.webdriver.common.by import By
import time
from sqlalchemy.orm import Session

from app.database import Vacancy
from app.schemas import Params
from urllib.parse import urlencode

from app.web_driver_manager import WebDriverManager


def build_url(params: Params) -> str:
    """Формирует URL для запроса."""
    query_params = {
        "text": params.keyword,
        "page": params.page,
        "experience": params.experience,
        "employment": params.employment,
        "schedule": params.schedule,
        "part_time": params.part_time,
        "salary": params.salary,
    }
    query_params = {k: v for k, v in query_params.items() if v}
    return f"https://hh.ru/search/vacancy?{urlencode(query_params)}"


def get_text_or_none(element, by, value):
    """Безопасно получает текст элемента."""
    try:
        return element.find_element(by, value).text
    except:
        return None


def parse_vacancies(driver):
    """Извлекает вакансии со страницы."""
    vacancies = []
    vacancy_elements = driver.find_elements(By.CLASS_NAME, "vacancy-card--z_UXteNo7bRGzxWVcL7y")

    for item in vacancy_elements:
        title = get_text_or_none(item, By.CLASS_NAME, "serp-item__title-link")
        link = item.find_element(By.CLASS_NAME, "bloko-link").get_attribute("href") if title else None
        vacancy_id = link.split("/")[-1] if link else None

        vacancy = {
            "id": vacancy_id,
            "title": title,
            "experience": get_text_or_none(item, By.CLASS_NAME, "label--rWRLMsbliNlu_OMkM_D3"),
            "link": link,
            "company": get_text_or_none(item, By.CLASS_NAME, "company-info-text--vgvZouLtf8jwBmaD1xgp"),
            "salary": get_text_or_none(item, By.CLASS_NAME, "fake-magritte-primary-text--Hdw8FvkOzzOcoR4xXWni"),
            "location": get_text_or_none(item, By.XPATH, ".//span[@data-qa='vacancy-serp__vacancy-address']"),
        }
        vacancies.append(vacancy)
    return vacancies


def save_vacancies_to_db(vacancies, session):
    """Сохраняет вакансии в БД, если их там нет."""
    for vacancy in vacancies:
        if not session.query(Vacancy).filter(Vacancy.id == vacancy["id"]).first():
            session.add(Vacancy(**vacancy))
    session.commit()


def search_vacancies(params: Params, session: Session):
    """Выполняет логику создания драйвера, создает url, парсит вакансии с сайта и выдает результат."""
    driver = WebDriverManager.create_chrome_driver()
    driver.get(build_url(params))
    time.sleep(5)
    vacancies = parse_vacancies(driver)
    driver.quit()
    save_vacancies_to_db(vacancies, session)
    return {"vacancies": vacancies}
