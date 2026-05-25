from flask import Blueprint, flash, redirect, url_for

from app.repositories.check_repository import CheckRepository
from app.repositories.url_repository import URLRepository
from app.services.check_service import CheckService

checks_bp = Blueprint("checks", __name__, url_prefix="/checks")


def get_check_service():
    url_repo = URLRepository()
    check_repo = CheckRepository()
    return CheckService(url_repo, check_repo)


@checks_bp.route("/url/<int:url_id>/run", methods=["POST"])
def run_check(url_id: int):
    check_service = get_check_service()
    success, message = check_service.perform_check(url_id)

    flash(message, "success" if success else "danger")
    return redirect(url_for("urls.details", id=url_id))
