from flask import Blueprint, flash, redirect, render_template, url_for

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.errorhandler(404)
def not_found(error):
    flash("Страница не найдена", "danger")
    return redirect(url_for("main.index"))


@main_bp.errorhandler(500)
def internal_error(error):
    flash("Внутренняя ошибка сервера", "danger")
    return redirect(url_for("main.index"))
