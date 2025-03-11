from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from chromedriver_py import binary_path


class WebDriverManager:
    """Класс для управления Selenium WebDriver."""

    @staticmethod
    def create_chrome_driver():
        """Функция для создания драйвера и управления Selenium WebDriver. """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        service = Service(binary_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
