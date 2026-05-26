from typing import Any

from page_analyzer.db import fetch_and_parse_url
from page_analyzer.models.check import URLChecker
from page_analyzer.repositories.check_repository import CheckRepository
from page_analyzer.repositories.url_repository import URLRepository


class CheckService:
    def __init__(
        self, url_repository: URLRepository, check_repository: CheckRepository
    ):
        self.url_repo = url_repository
        self.check_repo = check_repository

    def perform_check(self, url_id: int) -> tuple[bool, str]:
        url = self.url_repo.get_by_id(url_id)

        if not url:
            return False, "URL не найден"

        result = fetch_and_parse_url(url.name)

        if "error" in result:
            return False, "Произошла ошибка при проверке"

        check = URLChecker.from_parsed_result(url_id, result)
        self.check_repo.create(check)

        return True, "Страница успешно проверена"

    def get_check_history(self, url_id: int, limit: int | None = None) -> list:
        checks = self.check_repo.get_by_url_id(url_id)

        if limit:
            checks = checks[:limit]

        return checks

    def get_latest_check_status(self, url_id: int) -> dict[str, Any] | None:
        latest = self.check_repo.get_latest_for_url(url_id)

        if not latest:
            return None

        return {
            "status_code": latest.status_code,
            "checked_at": latest.created_at,
            "is_healthy": latest.is_successful,
        }
