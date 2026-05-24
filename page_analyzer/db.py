import os
from datetime import datetime

import psycopg
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    return conn


def get_url_by_id(url_id):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM urls WHERE id = %s", (url_id,))
        result = cur.fetchone()

        if not result:
            return None

        if isinstance(result, dict):
            return result.get("name")

        return result[0]

    finally:
        conn.close()


def fetch_and_parse_url(url):
    try:
        response = requests.get(url, timeout=5)
        if response.ok:
            soup = BeautifulSoup(response.content, "html.parser")
            return {
                "status_code": response.status_code,
                "title": (
                    soup.find("title").text.strip()
                    if soup.find("title")
                    else None
                ),
                "h1": soup.find("h1").text.strip() if soup.find("h1") else None,
                "description": (
                    soup.find("meta", attrs={"name": "description"})
                    .get("content")
                    .strip()
                    if soup.find("meta", attrs={"name": "description"})
                    else None
                ),
            }
        else:
            return {"error": f"Ошибка HTTP: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Ошибка сети: {str(e)}"}


def insert_url_check(url_id, data):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO url_checks 
               (url_id, status_code, h1, title, description, created_at) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                url_id,
                data["status_code"],
                data["h1"],
                data["title"],
                data["description"],
                datetime.now(),
            ),
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при вставке проверки: {e}")
    finally:
        conn.close()


def get_all_urls():
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT u.id, u.name, 
                   MAX(c.created_at) AS last_checked, 
                   MAX(c.status_code) AS last_status_code
            FROM urls u
            LEFT JOIN url_checks c ON u.id = c.url_id
            GROUP BY u.id
            ORDER BY u.created_at DESC
        """)
        return cur.fetchall()
    finally:
        conn.close()


def get_url_details(url_id):
    """Получает детали одного URL и список всех его проверок."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()

        cur.execute(
            "SELECT id, name, created_at FROM urls WHERE id = %s", (url_id,)
        )
        url_data = cur.fetchone()

        if not url_data:
            return None, None

        cur.execute(
            """
            SELECT id, status_code, h1, title, description, created_at 
            FROM url_checks 
            WHERE url_id = %s 
            ORDER BY created_at DESC
        """,
            (url_id,),
        )

        checks = cur.fetchall()

        return url_data, checks
    finally:
        conn.close()
