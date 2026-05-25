from urllib.parse import urlparse, urlunparse

import validators

from page_analyzer.config import get_config


class ValidationService:
    def __init__(self):
        self.config = get_config()

    def validate(self, url: str) -> tuple[bool, str] | None:
        """
        Validate URL.
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url or not url.strip():
            return False, "URL не может быть пустым"

        url = url.strip()

        if len(url) > self.config.max_url_length:
            return (
                False,
                f"URL слишком длинный (максимум {self.config.max_url_length} "
                f"символов)",
            )

        if not urlparse(url).scheme:
            url = f"http://{url}"

        if not validators.url(url):
            return False, "Некорректный URL"

        return True, None

    def normalize(self, url: str) -> str:
        """
        Normalize URL to canonical form.
        Example: https://Example.com/Path/ -> http://example.com
        """
        parsed = urlparse(url)
        scheme = parsed.scheme.lower() if parsed.scheme else "http"
        netloc = parsed.netloc.lower()

        if scheme == "http" and netloc.endswith(":80"):
            netloc = netloc[:-3]
        elif scheme == "https" and netloc.endswith(":443"):
            netloc = netloc[:-4]

        return urlunparse((scheme, netloc, "", "", "", ""))

    def extract_domain(self, url: str) -> str:
        parsed = urlparse(url)
        return parsed.netloc or parsed.path
