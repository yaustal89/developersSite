import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

PROJECT_DIR = Path(__file__).resolve().parent
JSON_FILE = PROJECT_DIR / "pik_projects_full.json"

def get_chrome_options() -> Options:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--enable-unsafe-swiftshader")
    return options

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
        print(f"Saved: {data['name']} | Метро: {data.get('metro', '-')}")
    else:
        print(f"Already exists: {data['name']}")

def parse_project_page(driver: webdriver.Chrome, url: str) -> Optional[Dict]:
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )

        name_el = driver.find_element(
            By.XPATH, 
            '//h1'
            )
        name = name_el.text.strip() if name_el else "Not found"

        description_el = driver.find_element(
            By.XPATH, 
            '//p[contains(@class, "sc-iPahhU") or contains(@class, "sc-hnCoju")]'
            )
        description = description_el.text.strip() if description_el else "Not found"
        

        return {
            "name": name,
            "url": url,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return None

def parse_pik_projects() -> None:
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=get_chrome_options()
        )
    main_url = "https://www.pik.ru/projects"
    driver.get(main_url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[contains(@class, "styles__ProjectCard")]'))
        )   

        cards = driver.find_elements(By.XPATH, '//a[contains(@class, "styles__ProjectCard")]')

        project_cards = []
        for card in cards:
            href = card.get_attribute("href")
            metro = card.find_element(By.XPATH, './/p[contains(@class, "styles__Metro")]').text.strip()
            project_cards.append({
                "href": href,
                "metro": metro
            })

        print(f"Projects found: {len(project_cards)}")
        projects_data = load_json_data(JSON_FILE)

        for item in project_cards:
            full_url = item['href']
            metro = item['metro']

            print(f"Going to: {full_url}")
            project_data = parse_project_page(driver, full_url)

            if project_data:
                project_data["metro"] = metro
                save_to_json(project_data, projects_data)

    finally:
        if driver:
            driver.quit()

def main():
    parse_pik_projects()

if __name__ == "__main__":
    main()

#TODO: deal with dynamic parsing