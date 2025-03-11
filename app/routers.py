from fastapi import FastAPI, Depends

from app.analytics import analytics_by_title, analytics_by_company
from app.database import Session, get_db
from app.schemas import Params
from app.service import search_vacancies

app = FastAPI()


@app.post("/vacancies")
def get_vacancies(params: Params, db: Session = Depends(get_db)):
    # Эндпоинт для поиска вакансий и их получения с использованием параметров и подключения к базе данных
    return search_vacancies(params, db)


@app.get("/analytics/title")
def get_analytics_title(title: str, db: Session = Depends(get_db)):
    # Эндпоинт для получения аналитики по ключевому слову
    return analytics_by_title(title, db)


@app.get("/analytics/company")
def get_analytics_company(company: str, db: Session = Depends(get_db)):
    # Эндпоинт для получения аналитики по названию компании
    return analytics_by_company(company, db)
