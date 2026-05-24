from urllib.parse import urlparse

import validators


def normalize_url(url: str) -> str:
    """
    Normalize URL: extract scheme and domain.
    Example: https://example.com/path?query -> https://example.com
    """
    parsed = urlparse(url)
    normalized = f"{parsed.scheme}://{parsed.netloc}"
    return normalized.lower()


def is_valid_url(url: str) -> bool:
    """
    Validate URL.
    Checks: not empty, length <= 255, valid URL format.
    """
    if not url or not isinstance(url, str):
        return False

    url = url.strip()

    if len(url) > 255:
        return False

    # Add scheme if missing for validation
    if not url.startswith(("http://", "https://")):
        test_url = "https://" + url
    else:
        test_url = url

    return validators.url(test_url)


def extract_domain(url: str) -> str:
    """Extract domain name from URL."""
    parsed = urlparse(url)
    return parsed.netloc
