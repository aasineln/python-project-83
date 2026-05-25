from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class URLChecker:
    id: int | None
    url_id: int
    status_code: int | None
    h1: str | None
    title: str | None
    description: str | None
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_parsed_result(
        cls, url_id: int, parsed_data: dict[str, Any]
    ) -> "URLChecker":
        return cls(
            id=None,
            url_id=url_id,
            status_code=parsed_data.get("status_code"),
            h1=parsed_data.get("h1"),
            title=parsed_data.get("title"),
            description=parsed_data.get("description"),
        )

    @property
    def is_successful(self) -> bool:
        return self.status_code and 200 <= self.status_code < 300
