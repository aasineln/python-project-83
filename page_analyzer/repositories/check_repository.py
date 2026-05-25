from page_analyzer.models.check import URLChecker
from page_analyzer.repositories.base import Repository, SQLBuilder


class CheckRepository(Repository):
    def get_by_id(self, id: int) -> URLChecker | None:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, url_id, status_code, h1, title, description, 
                      created_at
                    FROM url_checks WHERE id = %s
                    """,
                    (id,),
                )
                row = cur.fetchone()
                if row:
                    return URLChecker(
                        id=row["id"],
                        url_id=row["url_id"],
                        status_code=row["status_code"],
                        h1=row["h1"],
                        title=row["title"],
                        description=row["description"],
                        created_at=row["created_at"],
                    )
                return None

    def get_by_url_id(self, url_id: int) -> list[URLChecker]:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, url_id, status_code, h1, title, description, 
                    created_at
                    FROM url_checks WHERE url_id = %s
                    ORDER BY created_at DESC
                """,
                    (url_id,),
                )
                rows = cur.fetchall()
                return [
                    URLChecker(
                        id=row["id"],
                        url_id=row["url_id"],
                        status_code=row["status_code"],
                        h1=row["h1"],
                        title=row["title"],
                        description=row["description"],
                        created_at=row["created_at"],
                    )
                    for row in rows
                ]

    def create(self, check: URLChecker) -> URLChecker:
        query, params = SQLBuilder.insert(
            "url_checks",
            {
                "url_id": check.url_id,
                "status_code": check.status_code,
                "h1": check.h1,
                "title": check.title,
                "description": check.description,
                "created_at": check.created_at,
            },
        )

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                check_id = cur.fetchone()["id"]
                conn.commit()
                return URLChecker(
                    id=check_id,
                    url_id=check.url_id,
                    status_code=check.status_code,
                    h1=check.h1,
                    title=check.title,
                    description=check.description,
                    created_at=check.created_at,
                )

    def delete(self, id: int) -> bool:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM url_checks WHERE id = %s", (id,))
                conn.commit()
                return cur.rowcount > 0

    def get_latest_for_url(self, url_id: int) -> URLChecker | None:
        checks = self.get_by_url_id(url_id)
        return checks[0] if checks else None
