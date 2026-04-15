from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

import pandas as pd
import os
import re
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

# --- Configuración General ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
RUTA_BASE = os.environ.get("RUTA_BASE", os.path.dirname(os.path.abspath(__file__)))
URL_PRINCIPAL = "https://www.fondosdecultura.cl/convocatorias-abiertas/"

PALABRAS_CLAVE = [
    "antofagasta", "audiovisual", "diseño", "economía creativa",
    "formación", "interdisciplinas", "micsur", "libro y lectura",
    "música", "artes escénicas", "teatro"
]


def configure_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def is_relevant(text):
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in PALABRAS_CLAVE)


def extract_date_from_text(text):
    match = re.search(r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}", text, re.IGNORECASE)
    return match.group(0) if match else ""


def scrape_convocatorias(url, driver):
    convocatorias = []
    try:
        driver.get(url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
        )

        raw_links = []
        for link in driver.find_elements(By.TAG_NAME, "a"):
            try:
                text = link.text.strip()
                href = link.get_attribute("href")
                if text and href:
                    raw_links.append({"text": text, "href": href})
            except StaleElementReferenceException:
                print("Advertencia: elemento stale encontrado, se omite.")
                continue

        for link_info in raw_links:
            text = link_info["text"]
            href = link_info["href"]

            if is_relevant(text):
                convocatorias.append({
                    "Nombre": text,
                    "Fecha de Cierre": extract_date_from_text(text),
                    "URL": href
                })

    except TimeoutException:
        print(f"Error: La página en {url} tardó demasiado en cargar.")
    except Exception as e:
        print(f"Error inesperado durante el scraping: {e}")

    return convocatorias


def save_to_excel(data, base_path):
    if not data:
        print("No hay datos para guardar en Excel.")
        return False

    results_path = os.path.join(base_path, "resultados")
    os.makedirs(results_path, exist_ok=True)

    current_date = datetime.now().strftime("%Y-%m-%d")
    file_name = os.path.join(results_path, f"convocatorias_relevantes_{current_date}.xlsx")

    df = pd.DataFrame(data)
    df.to_excel(file_name, index=False)
    print(f"Se guardaron {len(df)} convocatorias en '{file_name}'.")
    return True


def send_telegram_message(data, token, chat_id):
    if not token or not chat_id:
        print("Error: TELEGRAM_TOKEN o TELEGRAM_CHAT_ID no están configurados.")
        return

    if not data:
        message = "No se encontraron convocatorias relevantes."
    else:
        message = "Convocatorias abiertas encontradas:\n\n"
        for conv in data:
            message += f"*{conv['Nombre']}*\n"
            message += f"📅 Cierra: {conv['Fecha de Cierre'] if conv['Fecha de Cierre'] else 'No especificada'}\n"
            message += f" {conv['URL']}\n\n"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Mensaje de Telegram enviado exitosamente.")
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar mensaje a Telegram: {e}")


# --- Ejecución Principal ---
if __name__ == "__main__":
    driver = configure_driver()
    try:
        convocatorias = scrape_convocatorias(URL_PRINCIPAL, driver)
    finally:
        driver.quit()

    save_to_excel(convocatorias, RUTA_BASE)
    send_telegram_message(convocatorias, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
