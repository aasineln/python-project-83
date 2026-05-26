from page_analyzer.models.check import URLChecker
from page_analyzer.models.url import URL


class TestURL:

    def test_url_creation(self):
        url = URL(id=1, name="https://example.com", created_at="2024-01-01")
        assert url.id == 1
        assert url.name == "https://example.com"
        assert url.created_at == "2024-01-01"

    def test_url_str_representation(self):
        url = URL(id=1, name="https://example.com", created_at="2024-01-01")
        assert str(url) == "https://example.com"


class TestCheck:

    def test_check_creation(self):
        check = URLChecker(
            id=1,
            url_id=1,
            status_code=200,
            h1="Title",
            title="Page Title",
            description="Description",
            created_at="2024-01-01",
        )
        assert check.id == 1
        assert check.url_id == 1
        assert check.status_code == 200
        assert check.h1 == "Title"
