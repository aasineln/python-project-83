from datetime import datetime


def format_date(value: datetime, format: str = "%Y-%m-%d") -> str:
    if value is None:
        return ""
    return value.strftime(format)
