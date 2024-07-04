from typing import Optional, Union
from pydantic import BaseModel
from selenium import webdriver
from chromedriver_py import binary_path
from fastapi import FastAPI, Depends
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from sqlalchemy.orm import Session
from app.analytics import analytics_by_title, analytics_by_company
from app.database import Vacancy, get_db

app = FastAPI()


experiences = ["doesNotMatter", "noExperience", "between1And3", "between3And6", "moreThan6"]
employment = ["full", "part", "project", "volunteer", "probation"]
schedules = ["fullDay", "shift", "flexible", "remote", "flyInFlyOut"]
part_times = ["employment_project", "employment_part", "from_four_to_six_hours_in_a_day", "only_saturday_and_sunday", "start_after_sixteen"]


class Params(BaseModel):
    keyword: str
    page: int = 0
    experience: Optional[str] = "doesNotMatter"
    employment: Optional[str]
    schedule: Optional[str]
    part_time: Optional[str]
    salary: Union[str, int, None]


def build_url(params: Params) -> str:
    url_parts = [
        f"text={params.keyword}",
        f"page={params.page}",
        f"experience={params.experience}"
    ]
    if params.employment:
        url_parts.append(f"employment={params.employment}")
    if params.schedule:
        url_parts.append(f"schedule={params.schedule}")
    if params.part_time:
        url_parts.append(f"part_time={params.part_time}")
    if params.salary:
        url_parts.append(f"salary={str(params.salary)}")

    return f"https://hh.ru/search/vacancy?{'&'.join(url_parts)}"


def search_vacancies(params, session):
    service = webdriver.ChromeService(executable_path=binary_path)
    driver = webdriver.Chrome(service=service)

    url = build_url(params)
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver.get(url)
    time.sleep(5)  # ожидание загрузки страницы
    vacancies = []
    items = driver.find_elements(By.CLASS_NAME, "vacancy-card--z_UXteNo7bRGzxWVcL7y")
    for item in items:
        title_element = item.find_element(By.CLASS_NAME, "serp-item__title-link")
        title = title_element.text

        vacancy_id = None
        try:
            link = item.find_element(By.CLASS_NAME, "bloko-link").get_attribute("href")
            vacancy_id = link.split('/')[-1]
        except:
            link = None
        if not link:
            link = None

        try:
            company = item.find_element(By.CLASS_NAME, "company-info-text--vgvZouLtf8jwBmaD1xgp").text
        except:
            company = None
        if not company:
            company = None

        try:
            salary = item.find_element(By.CLASS_NAME, "fake-magritte-primary-text--Hdw8FvkOzzOcoR4xXWni").text
        except:
            salary = None
        if not salary:
            salary = None

        try:
            experience = item.find_element(By.CLASS_NAME, "label--rWRLMsbliNlu_OMkM_D3").text
        except:
            experience = None
        if not experience:
            experience = None

        try:
            location = item.find_element(By.XPATH, ".//span[@data-qa='vacancy-serp__vacancy-address']").text
        except:
            location = None
        if not location:
            location = None
        existing_vacancy = False
        if vacancy_id:
            existing_vacancy = session.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
        if not existing_vacancy:
            vacancy_id = link.split('/')[-1] if link else None
            vacancy = Vacancy(
                id=vacancy_id,
                title=title,
                experience=experience,
                link=link,
                company=company,
                salary=salary,
                location=location
            )
            session.add(vacancy)
            session.commit()

        vacancies.append({
            "title": title,
            "experience": experience,
            "link": link,
            "company": company,
            "salary": salary,
            "location": location
        })

    driver.quit()
    return {"vacancies": vacancies}


@app.post("/vacancies")
def get_vacancies(params: Params, db: Session = Depends(get_db)):
    return search_vacancies(params, db)


@app.get("/analytics/title")
def get_analytics_title(title: str, db: Session = Depends(get_db)):
    return analytics_by_title(title, db)


@app.get("/analytics/company")
def get_analytics_company(company: str, db: Session = Depends(get_db)):
    return analytics_by_company(company, db)