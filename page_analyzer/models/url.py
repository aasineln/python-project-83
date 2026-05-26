from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class URL:
    id: int | None
    name: str
    created_at: datetime = field(default_factory=datetime.now)

    def __str__(self):
        return self.name if self.name else ""

    def __post_init__(self):
        if not self.name or len(self.name) > 255:
            raise ValueError("Invalid URL name")

    @property
    def domain(self) -> str:
        from urllib.parse import urlparse

        parsed = urlparse(self.name)
        return parsed.netloc or parsed.path

    @property
    def is_valid(self) -> bool:
        import validators

        return bool(validators.url(self.name))

    def normalize(self) -> "URL":
        from urllib.parse import urlparse, urlunparse

        parsed = urlparse(self.name)
        scheme = parsed.scheme.lower() or "http"
        netloc = parsed.netloc.lower()
        normalized_name = urlunparse((scheme, netloc, "", "", "", ""))

        return URL(id=self.id, name=normalized_name, created_at=self.created_at)
