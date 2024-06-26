from fastapi import FastAPI, HTTPException
from bs4 import BeautifulSoup
import requests

app = FastAPI()


@app.get("/vacancies/{keyword}")
async def get_vacancies(keyword: str):
    url = f"https://hh.ru/search/vacancy?text={keyword}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to retrieve data")

    soup = BeautifulSoup(response.text, "html.parser")
    vacancies = []

    for item in soup.find_all("div", class_="vacancy-serp-item"):
        title = item.find("a", class_="bloko-link").text.strip()
        link = item.find("a", class_="bloko-link")["href"]
        company = item.find("a", class_="bloko-link_secondary").text.strip() if item.find("a", class_="bloko-link_secondary") else "Не указано"
        salary = item.find("div", class_="vacancy-serp-item__sidebar").text.strip() if item.find("div", class_="vacancy-serp-item__sidebar") else "Не указана"
        vacancies.append({
            "title": title,
            "link": link,
            "company": company,
            "salary": salary
        })

    return {"vacancies": vacancies}