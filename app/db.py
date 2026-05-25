import os

import psycopg
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from psycopg import Connection
from psycopg.rows import dict_row

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
MAX_TEXT_LENGTH = 200


def get_db_connection() -> Connection:
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    return conn


def fetch_and_parse_url(url: str) -> dict:
    def truncate(text: str | None) -> str | None:
        if not text:
            return None
        text = text.strip()
        if len(text) <= MAX_TEXT_LENGTH:
            return text
        return f"{text[:MAX_TEXT_LENGTH]}..."

    try:
        response = requests.get(url, timeout=5)
        if response.ok:
            soup = BeautifulSoup(response.content, "html.parser")
            title_elem = soup.find("title")
            h1_elem = soup.find("h1")
            meta_elem = soup.find("meta", attrs={"name": "description"})

            return {
                "status_code": response.status_code,
                "title": truncate(title_elem.text) if title_elem else None,
                "h1": truncate(h1_elem.text) if h1_elem else None,
                "description": (
                    truncate(meta_elem.get("content")) if meta_elem else None
                ),
            }
        else:
            return {"error": f"Ошибка HTTP: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Ошибка сети: {str(e)}"}
