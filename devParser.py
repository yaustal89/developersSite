import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

JSON_FILE = 'pik_projects_full.json'

def load_json_data():
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_to_json(data, projects):
    existing_names = {item['name'] for item in projects}

    if data['name'] not in existing_names:
        projects.append(data)
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(projects, f, ensure_ascii=False, indent=4)
        print(f"Сохранено в JSON: {data['name']} | Метро: {data.get('metro', '-')}")
    else:
        print(f"Уже есть: {data['name']}")

def parse_project_page(driver, url):
    """Парсим данные со страницы конкретного проекта"""
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )

        name = driver.find_element(By.XPATH, '//h1').text.strip() if driver.find_elements(By.XPATH, '//h1') else "Не найдено"

        metro_els = driver.find_elements(By.XPATH, '//p[contains(text(), "метро")]')
        metro = metro_els[0].text.replace("метро", "").strip() if metro_els else None

        description_els = driver.find_elements(By.XPATH, '//p[contains(@class, "sc-iPahhU ceQaiZ")]')
        description = description_els[0].text.strip() if description_els else None

        print("Найдено description_els:", len(description_els))
        if description_els:
            print("Текст первого элемента:", description_els[0].text)
        else:
            print("Элементы не найдены")

        return {
            "name": name,
            "url": url,
            "metro": metro,
            "description": description if description else None,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"❌ Ошибка при парсинге страницы {url}: {e}")
        return None

def parse_pik_projects():
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
            metro_el = card.find_element(By.XPATH, './/p[contains(@class, "styles__Metro-vea7eb-3 iqDCzF")]')
            metro = metro_el.text.strip() if metro_el else None
            project_cards.append({
                "href": href,
                "metro": metro
            })

        print(f"Найдено карточек: {len(project_cards)}")
        projects_data = load_json_data()

        for href in project_cards:
            href = href['href']

            print(f"Переход по ссылке: {href}")
            driver.get(href)

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'body'))
                )

                name = driver.find_element(By.XPATH, '//h1').text.strip() if driver.find_elements(By.XPATH, '//h1') else "Не найдено"

                description_els = driver.find_elements(By.XPATH, '//p[contains(@class, "sc-iPahhU ceQaiZ")]')
                description = description_els[0].text.strip() if description_els else None

                project_data = {
                    "name": name,
                    "url": href,
                    "metro": metro,
                    "description": description,
                    "timestamp": datetime.now().isoformat()
                }

                if project_data['name'] != "Не найдено":
                    save_to_json(project_data, projects_data)
                    projects_data = load_json_data()
                else:
                    print("Не удалось получить название ЖК")

            except Exception as e:
                print(f"Ошибка при парсинге страницы {href}: {e}")

            driver.get(main_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//a[contains(@class, "styles__ProjectCard")]'))
            )

    finally:
        driver.quit()

if __name__ == "__main__":
    parse_pik_projects()

#TODO: metro