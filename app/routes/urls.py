from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.repositories.check_repository import CheckRepository
from app.repositories.url_repository import URLRepository
from app.services.url_service import URLService
from app.services.validation_service import ValidationService

urls_bp = Blueprint("urls", __name__, url_prefix="/urls")


def get_url_service():
    url_repo = URLRepository()
    check_repo = CheckRepository()
    validation_service = ValidationService()
    return URLService(url_repo, check_repo, validation_service)


@urls_bp.route("/")
def list_urls():
    url_service = get_url_service()
    urls_data = url_service.get_all_urls_with_status()
    return render_template("urls.html", urls=urls_data)


@urls_bp.route("/<int:id>")
def details(id: int):
    url_service = get_url_service()
    url, checks = url_service.get_url_with_checks(id)

    if not url:
        flash("URL не найден", "danger")
        return redirect(url_for("index"))

    stats = url_service.get_url_statistics(id)

    return render_template("url.html", url=url, checks=checks, statistics=stats)


@urls_bp.route("/add", methods=["POST"])
def add():
    url_input = request.form.get("url", "").strip()

    url_service = get_url_service()
    url, flash_message, flash_category = url_service.add_url(url_input)

    flash(flash_message, flash_category)

    if url:
        return redirect(url_for("urls.details", id=url.id))
    return redirect(url_for("main.index"))
