from typing import Any

from page_analyzer.models.url import URL
from page_analyzer.repositories.base import Repository, SQLBuilder


class URLRepository(Repository):
    def get_by_id(self, id: int) -> URL | None:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name, created_at FROM urls WHERE id = %s", (id,)
                )
                row = cur.fetchone()
                if row:
                    return URL(
                        id=row["id"],
                        name=row["name"],
                        created_at=row["created_at"],
                    )
                return None

    def get_by_name(self, name: str) -> URL | None:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name, created_at FROM urls WHERE name = %s",
                    (name,),
                )
                row = cur.fetchone()
                if row:
                    return URL(
                        id=row["id"],
                        name=row["name"],
                        created_at=row["created_at"],
                    )
                return None

    def get_all_with_last_check(self) -> list[dict[str, Any]]:
        """Get all URLs with their last check info."""
        query = """
            SELECT 
                u.id, 
                u.name, 
                u.created_at,
                MAX(uc.created_at) as last_checked,
                MAX(uc.status_code) AS last_status_code
            FROM urls u
            LEFT JOIN url_checks uc ON u.id = uc.url_id
            GROUP BY u.id, uc.status_code
            ORDER BY u.created_at DESC
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return [dict(row) for row in cur.fetchall()]

    def create(self, url: URL) -> URL:
        normalized = url.normalize()
        query, params = SQLBuilder.insert(
            "urls",
            {"name": normalized.name, "created_at": normalized.created_at},
        )

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                url_id = cur.fetchone()["id"]
                conn.commit()
                return URL(
                    id=url_id,
                    name=normalized.name,
                    created_at=normalized.created_at,
                )

    def delete(self, id: int) -> bool:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM urls WHERE id = %s", (id,))
                conn.commit()
                return cur.rowcount > 0

    def exists(self, name: str) -> bool:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM urls WHERE name = %s LIMIT 1", (name,)
                )
                return cur.fetchone() is not None
