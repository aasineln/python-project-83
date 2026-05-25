from datetime import datetime

from page_analyzer.repositories.check_repository import CheckRepository
from page_analyzer.repositories.url_repository import URLRepository
from page_analyzer.services.url_service import URLService
from page_analyzer.services.validation_service import ValidationService


def get_url_service():
    url_repo = URLRepository()
    check_repo = CheckRepository()
    validation_service = ValidationService()
    return URLService(url_repo, check_repo, validation_service)


def format_date(value: datetime, format: str = "%Y-%m-%d") -> str:
    if value is None:
        return ""
    return value.strftime(format)
