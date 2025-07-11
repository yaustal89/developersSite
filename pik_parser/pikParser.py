import json
from pathlib import Path
from datetime import datetime
from typing import Union, List, Dict

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

PROJECT_DIR = Path(__file__).resolve().parent
JSON_FILE = PROJECT_DIR / "pik_projects_full.json"

def load_json_data(JSON_FILE: Path) -> List[Dict]:
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_to_json(data: dict, projects: list) -> None:
    existing_names = {item['name'] for item in projects}

    if data['name'] not in existing_names:
        projects.append(data)
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(projects, f, ensure_ascii=False, indent=4)
        print(f"Сохранено в JSON: {data['name']} | Метро: {data.get('metro', '-')}")
    else:
        print(f"Уже есть: {data['name']}")

def parse_project_page(driver: webdriver.Chrome, url: str) -> Union[dict,list]:
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )

        name_els = driver.find_elements(By.XPATH, '//h1')
        name = name_els[0].text.strip() if name_els else "Not found"

        description_els = driver.find_elements(By.XPATH, 
                                               '//p[contains(@class, "sc-iPahhU ceQaiZ")] | '
                                               '//p[contains(@class, "sc-dWTlHi fDHbzI")]')
        description = description_els[0].text.strip() if description_els else None

        return {
            "name": name,
            "url": url,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return []

def parse_pik_projects() -> None:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--enable-unsafe-swiftshader")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    main_url = "https://www.pik.ru/projects "
    driver.get(main_url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[contains(@class, "styles__ProjectCard")]'))
        )

        cards = driver.find_elements(By.XPATH, '//a[contains(@class, "styles__ProjectCard")]')

        project_cards = []
        for card in cards:
            href = card.get_attribute("href")
            metro_el = card.find_element(By.XPATH, './/p[contains(@class, "styles__Metro")]')
            metro = metro_el.text.strip() if metro_el else None
            project_cards.append({
                "href": href,
                "metro": metro
            })

        print(f"Найдено карточек: {len(project_cards)}")
        projects_data = load_json_data(JSON_FILE)

        for item in project_cards:
            full_url = item['href']
            metro = item['metro']

            print(f"Переход по ссылке: {full_url}")
            project_data = parse_project_page(driver, full_url)

            if project_data and project_data["name"] != "Not found":
                project_data["metro"] = metro
                save_to_json(project_data, projects_data)
                projects_data = load_json_data(JSON_FILE)
            else:
                print("Не удалось спарсить данные")

            driver.get(main_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//a[contains(@class, "styles__ProjectCard")]'))
            )

    finally:
        driver.quit()

if __name__ == "__main__":
    parse_pik_projects()