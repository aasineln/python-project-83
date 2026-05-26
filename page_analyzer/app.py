import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from page_analyzer.repositories.check_repository import CheckRepository
from page_analyzer.repositories.url_repository import URLRepository
from page_analyzer.services.check_service import CheckService
from page_analyzer.utils import format_date, get_url_service

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "your_secret_key")
app.jinja_env.filters["date"] = format_date

url_service = get_url_service()
url_repo = URLRepository()
check_repo = CheckRepository()
check_service = CheckService(url_repo, check_repo)


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/urls/<int:url_id>/checks", methods=["POST"])
def checks(url_id: int):
    success, message = check_service.perform_check(url_id)

    flash(message, "success" if success else "danger")
    return redirect(url_for("details", url_id=url_id))


@app.route("/urls")
def list_urls():
    urls_data = url_service.get_all_urls_with_status()
    for url in urls_data:
        if "last_checked" not in url:
            url["last_checked"] = None

    return render_template("urls.html", urls=urls_data)


@app.route("/urls/<int:url_id>")
def details(url_id: int):
    url, checks = url_service.get_url_with_checks(url_id)

    if not url:
        flash("URL не найден", "danger")
        return redirect(url_for("index"))

    stats = url_service.get_url_statistics(url_id)

    return render_template("url.html", url=url, checks=checks, statistics=stats)


@app.route("/urls", methods=["POST"], endpoint="urls")
def add_url():
    url_input = request.form.get("url", "").strip()

    url, flash_message, flash_category = url_service.add_url(url_input)
    flash(flash_message, flash_category)

    if url:
        return redirect(url_for("details", url_id=url.id))
    return render_template("index.html"), 422
