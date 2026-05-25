from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Generator

from page_analyzer.db import get_db_connection


class Repository(ABC):
    @contextmanager
    def _get_connection(self) -> Generator:
        conn = None
        try:
            conn = get_db_connection()
            yield conn
        finally:
            if conn:
                conn.close()

    @abstractmethod
    def get_by_id(self, id: int) -> Any | None:
        pass

    @abstractmethod
    def create(self, entity: Any) -> Any:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass


class SQLBuilder:
    @staticmethod
    def insert(table: str, data: dict[str, Any]) -> tuple:
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = (
            f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) "
            f"RETURNING id"
        )
        return query, tuple(data.values())

    @staticmethod
    def update(table: str, id: int, data: dict[str, Any]) -> tuple:
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE id = %s"
        return query, tuple(list(data.values()) + [id])
