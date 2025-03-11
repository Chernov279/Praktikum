from typing import Union
from forex_python.converter import CurrencyCodes
import requests
from bs4 import BeautifulSoup

class CurrencyConverter:
    """Класс для конвертации валюты в рубли"""

    @staticmethod
    def get_currency_rate_parser(currency_code):
        url = f"https://cbr.ru/currency_base/daily/"
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', class_='data')
            rows = table.find_all('tr')

            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    currency = cols[1].text.strip()
                    rate_rub = cols[-1].text.strip().replace(",", ".")
                    rate_currency = cols[2].text.strip().replace(",", ".")

                    if currency == currency_code:
                        return round(float(rate_rub) / float(rate_currency), 2)

    @staticmethod
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
            currency_rate = CurrencyConverter.get_currency_rate_parser(currency_code)
            if currency_rate and amount:
                return round(float(currency_rate) * amount, 2)