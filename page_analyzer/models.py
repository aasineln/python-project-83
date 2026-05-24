from datetime import datetime
from typing import Dict, List, Optional

import psycopg
from psycopg.rows import dict_row


class URLModel:
    def __init__(self, database_url: str):
        self.database_url = database_url

    def get_connection(self):
        return psycopg.connect(self.database_url, row_factory=dict_row)

    def add_url(self, name: str) -> Optional[int]:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM urls WHERE name = %s", (name,))
                    existing = cur.fetchone()

                    if existing:
                        return existing["id"]

                    cur.execute(
                        "INSERT INTO urls (name, created_at) "
                        "VALUES (%s, %s) RETURNING id",
                        (name, datetime.now()),
                    )
                    result = cur.fetchone()
                    return result["id"] if result else None

        except Exception as e:
            print(f"Error adding URL: {e}")
            return None

    def get_all_urls(self) -> List[Dict]:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id, name, created_at "
                        "FROM urls ORDER BY created_at DESC"
                    )
                    urls = cur.fetchall()
                    return urls if urls else []
        except Exception as e:
            print(f"Error getting all URLs: {e}")
            return []

    def get_url_by_id(self, url_id: int) -> Optional[Dict]:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id, name, created_at FROM urls WHERE id = %s",
                        (url_id,),
                    )
                    url = cur.fetchone()
                    return url
        except Exception as e:
            print(f"Error getting URL by ID: {e}")
            return None

    def url_exists(self, name: str) -> bool:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM urls WHERE name = %s", (name,))
                    exists = cur.fetchone() is not None
                    return exists
        except Exception as e:
            print(f"Error checking URL existence: {e}")
            return False
