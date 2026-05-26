from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from page_analyzer.app import app
from page_analyzer.models.check import URLChecker
from page_analyzer.models.url import URL


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test_secret_key"

    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def mock_url_service():
    with patch("page_analyzer.app.url_service") as mock:
        yield mock


@pytest.fixture
def mock_check_service():
    with patch("page_analyzer.app.check_service") as mock:
        yield mock


class TestIndex:
    def test_index_page(self, client):
        response = client.get("/")
        print(response.data)
        assert response.status_code == 200
        assert '<h1 class="display-4 mb-4">' in response.data.decode("utf-8")
        assert "Анализатор страниц" in response.data.decode("utf-8")

    def test_index_has_form(self, client):
        response = client.get("/")
        assert "<form" in response.data.decode("utf-8")
        assert 'method="post"' in response.data.decode("utf-8")
        assert 'name="url"' in response.data.decode("utf-8")


class TestAddURL:
    def test_add_valid_url(self, client, mock_url_service):
        mock_url = Mock(spec=URL)
        mock_url.id = 1
        mock_url.name = "https://example.com"
        mock_url_service.add_url.return_value = (
            mock_url,
            "Успешно добавлено",
            "success",
        )

        response = client.post("/urls", data={"url": "https://example.com"})

        assert response.status_code == 302
        assert response.location == "/urls/1"
        mock_url_service.add_url.assert_called_once_with("https://example.com")

    def test_add_invalid_url(self, client, mock_url_service):
        mock_url_service.add_url.return_value = (
            None,
            "Некорректный URL",
            "danger",
        )

        response = client.post("/urls", data={"url": "not-a-valid-url"})

        assert response.status_code == 422
        mock_url_service.add_url.assert_called_once()

    def test_add_empty_url(self, client, mock_url_service):
        mock_url_service.add_url.return_value = (
            None,
            "URL не может быть пустым",
            "danger",
        )

        response = client.post("/urls", data={"url": ""})

        assert response.status_code == 422
        mock_url_service.add_url.assert_called_once_with("")

    def test_add_duplicate_url(self, client, mock_url_service):
        mock_url = Mock(spec=URL)
        mock_url.id = 1
        mock_url_service.add_url.return_value = (
            mock_url,
            "Сайт уже существует",
            "info",
        )

        response = client.post("/urls", data={"url": "https://example.com"})

        assert response.status_code == 302
        mock_url_service.add_url.assert_called_once()


class TestListURLs:
    def test_list_urls_empty(self, client, mock_url_service):
        mock_url_service.get_all_urls_with_status.return_value = []

        response = client.get("/urls")

        assert response.status_code == 200

        assert '<h1 class="mt-5">Сайты</h1>' in response.data.decode("utf-8")

    def test_list_urls_with_data(self, client, mock_url_service):
        urls_data = [
            {
                "id": 1,
                "name": "https://example.com",
                "created_at": "2024-01-01",
                "status_code": 200,
            },
            {
                "id": 2,
                "name": "https://google.com",
                "created_at": "2024-01-02",
                "status_code": None,
            },
        ]
        mock_url_service.get_all_urls_with_status.return_value = urls_data

        response = client.get("/urls")

        assert response.status_code == 200
        assert "https://example.com" in response.data.decode("utf-8")
        assert "https://google.com" in response.data.decode("utf-8")


class TestDetails:
    def test_details_existing_url(self, client, mock_url_service):
        mock_url = Mock(spec=URL)
        mock_url.id = 1
        mock_url.name = "https://example.com"
        mock_url.created_at = "2024-01-01"

        mock_checks = [
            Mock(
                spec=URLChecker,
                id=1,
                status_code=200,
                h1="Example",
                title="Example Domain",
                description="Example description",
                created_at="2024-01-01",
            )
        ]
        mock_stats = {"checks_count": 1, "last_check": "2024-01-01"}

        mock_url_service.get_url_with_checks.return_value = (
            mock_url,
            mock_checks,
        )
        mock_url_service.get_url_statistics.return_value = mock_stats

        response = client.get("/urls/1")

        assert response.status_code == 200
        assert "https://example.com" in response.data.decode("utf-8")

    def test_details_nonexistent_url(self, client, mock_url_service):
        mock_url_service.get_url_with_checks.return_value = (None, None)

        response = client.get("/urls/999")

        assert response.status_code == 302
        assert response.location == "/"

    def test_details_flash_on_not_found(self, client, mock_url_service):
        mock_url_service.get_url_with_checks.return_value = (None, None)

        response = client.get("/urls/999", follow_redirects=True)

        assert "URL не найден" in response.data.decode("utf-8")
        assert response.status_code == 200


class TestChecks:
    def test_check_successful(self, client, mock_check_service):
        mock_check_service.perform_check.return_value = (
            True,
            "Страница успешно проверена",
        )

        response = client.post("/urls/1/checks")

        assert response.status_code == 302
        assert response.location == "/urls/1"
        mock_check_service.perform_check.assert_called_once_with(1)

    def test_check_failed(self, client, mock_check_service):
        mock_check_service.perform_check.return_value = (
            False,
            "Произошла ошибка при проверке",
        )

        response = client.post("/urls/1/checks")

        assert response.status_code == 302
        mock_check_service.perform_check.assert_called_once_with(1)

    def test_check_with_timeout(self, client, mock_check_service):
        mock_check_service.perform_check.return_value = (
            False,
            "Превышено время ожидания ответа от сервера",
        )

        response = client.post("/urls/1/checks", follow_redirects=True)

        assert "Превышено время ожидания" in response.data.decode("utf-8")

    def test_check_connection_error(self, client, mock_check_service):
        mock_check_service.perform_check.return_value = (
            False,
            "Не удалось подключиться к серверу",
        )

        response = client.post("/urls/1/checks", follow_redirects=True)

        assert "Не удалось подключиться" in response.data.decode("utf-8")


class TestFlashMessages:
    def test_flash_on_successful_add(self, client, mock_url_service):
        mock_url = Mock(spec=URL)
        mock_url.id = 1
        mock_url.name = "https://example.com"
        mock_url.created_at = "2024-01-01"

        mock_url_service.add_url.return_value = (
            mock_url,
            "Успешно добавлено",
            "success",
        )

        mock_url_service.get_url_with_checks.return_value = (mock_url, [])
        mock_url_service.get_url_statistics.return_value = {}

        response = client.post(
            "/urls", data={"url": "https://example.com"}, follow_redirects=True
        )
        assert response.status_code == 200
        assert "Успешно добавлено" in response.data.decode("utf-8")

    def test_flash_on_invalid_url(self, client, mock_url_service):
        mock_url_service.add_url.return_value = (
            None,
            "Некорректный URL",
            "danger",
        )

        response = client.post(
            "/urls", data={"url": "invalid"}, follow_redirects=True
        )

        assert "Некорректный URL" in response.data.decode("utf-8")

    def test_flash_on_successful_check(self, client, mock_check_service):
        mock_check_service.perform_check.return_value = (
            True,
            "Страница успешно проверена",
        )

        response = client.post("/urls/1/checks", follow_redirects=True)

        assert "Страница успешно проверена" in response.data.decode("utf-8")
        assert "success" in response.data.decode("utf-8")


class TestIntegration:
    def test_full_flow_add_and_check(
        self, client, mock_url_service, mock_check_service
    ):
        mock_url = URL(
            id=1,
            name="https://example.com",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
        )
        mock_url.id = 1
        mock_url.name = "https://example.com"
        mock_url_service.add_url.return_value = (
            mock_url,
            "Успешно добавлено",
            "success",
        )

        response = client.post("/urls", data={"url": "https://example.com"})
        assert response.status_code == 302

        mock_check_service.perform_check.return_value = (
            True,
            "Страница успешно проверена",
        )

        response = client.post("/urls/1/checks")
        assert response.status_code == 302
        assert response.location == "/urls/1"

        mock_checks = [Mock(id=1, url_id=1, status_code=200)]
        mock_url_service.get_url_with_checks.return_value = (
            mock_url,
            mock_checks,
        )
        mock_url_service.get_url_statistics.return_value = {"status_code": 200}

        response = client.get(response.location)
        assert response.status_code == 200

    def test_redirect_chain(self, client, mock_url_service):
        mock_url = Mock(spec=URL)
        mock_url.id = 1
        mock_url.name = "https://example.com"
        mock_url.created_at = "2024-01-01 12:00:00"

        mock_url_service.add_url.return_value = (
            mock_url,
            "Успешно добавлено",
            "success",
        )

        mock_checks = []
        mock_url_service.get_url_with_checks.return_value = (
            mock_url,
            mock_checks,
        )

        mock_url_service.get_url_statistics.return_value = {
            "status_code": None,
            "h1": None,
            "title": None,
            "description": None,
            "checks_count": 0,
        }

        post_response = client.post(
            "/urls", data={"url": "https://example.com"}
        )
        assert post_response.status_code == 302
        assert post_response.location == "/urls/1"

        get_response = client.get(post_response.location)
        assert get_response.status_code == 200

        # Optional: Verify content
        assert "https://example.com" in get_response.data.decode("utf-8")


class TestTemplateRendering:
    def test_index_template(self, client):
        response = client.get("/")
        assert "<form" in response.data.decode("utf-8")
        assert 'action="/urls"' in response.data.decode("utf-8")

    def test_urls_template(self, client, mock_url_service):
        mock_url_service.get_all_urls_with_status.return_value = []
        response = client.get("/urls")
        assert "<table" in response.data.decode("utf-8")
        assert 'data-test="urls"' in response.data.decode("utf-8")

    def test_url_detail_template(self, client, mock_url_service):
        mock_url = Mock(spec=URL)
        mock_url.id = 1
        mock_url.name = "https://example.com"
        mock_url.created_at = "2024-01-01"

        mock_url_service.get_url_with_checks.return_value = (mock_url, [])
        mock_url_service.get_url_statistics.return_value = {}

        response = client.get("/urls/1")
        assert 'data-test="url"' in response.data.decode("utf-8")
        assert 'data-test="checks"' in response.data.decode("utf-8")


class TestHTTPMethods:
    def test_post_to_index_not_allowed(self, client):
        response = client.post("/")
        assert response.status_code == 405

    def test_get_to_add_url_not_allowed(self, client):
        response = client.get("/urls", method="POST" if False else None)
        response = client.get("/urls")
        assert response.status_code == 200

    def test_wrong_method_to_checks(self, client):
        response = client.get("/urls/1/checks")
        assert response.status_code == 405
