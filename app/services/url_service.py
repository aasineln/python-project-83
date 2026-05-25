from datetime import datetime
from typing import Any

from app.models.check import URLChecker
from app.models.url import URL
from app.repositories.check_repository import CheckRepository
from app.repositories.url_repository import URLRepository
from app.services.validation_service import ValidationService


class URLService:
    def __init__(
        self,
        url_repository: URLRepository,
        check_repository: CheckRepository,
        validation_service: ValidationService,
    ):
        self.url_repo = url_repository
        self.check_repo = check_repository
        self.validator = validation_service

    def add_url(self, raw_url: str) -> tuple[URL | None, str, str]:
        is_valid, error = self.validator.validate(raw_url)
        if not is_valid:
            return None, error, "danger"

        normalized_name = self.validator.normalize(raw_url)

        existing_url = self.url_repo.get_by_name(normalized_name)
        if existing_url:
            return existing_url, "Страница уже существует", "warning"

        new_url = URL(id=None, name=normalized_name, created_at=datetime.now())

        try:
            created_url = self.url_repo.create(new_url)
            return created_url, "Страница успешно добавлена", "success"
        except Exception as e:
            print(f"Error creating URL: {e}")
            return None, "Произошла ошибка при добавлении", "danger"

    def get_url_with_checks(
        self, url_id: int
    ) -> tuple[URL | None, list[URLChecker]]:
        url = self.url_repo.get_by_id(url_id)
        if not url:
            return None, []

        checks = self.check_repo.get_by_url_id(url_id)
        return url, checks

    def get_all_urls_with_status(self) -> list[dict[str, Any]]:
        return self.url_repo.get_all_with_last_check()

    def get_url_statistics(self, url_id: int) -> dict[str, Any]:
        checks = self.check_repo.get_by_url_id(url_id)

        if not checks:
            return {
                "total_checks": 0,
                "successful_checks": 0,
                "average_status": None,
                "last_check": None,
            }

        successful = [c for c in checks if c.is_successful]

        return {
            "total_checks": len(checks),
            "successful_checks": len(successful),
            "success_rate": (len(successful) / len(checks)) * 100,
            "average_status": sum(
                c.status_code for c in checks if c.status_code
            )
            / len(checks),
            "last_check": checks[0].created_at if checks else None,
        }
