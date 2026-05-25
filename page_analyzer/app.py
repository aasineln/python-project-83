import os
from urllib.parse import urlparse

import validators
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from .db import (
    fetch_and_parse_url,
    get_all_urls,
    get_db_connection,
    get_url_by_id,
    get_url_details,
    insert_url_check,
)
from .utils import format_date

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "your_secret_key")
app.jinja_env.filters["date"] = format_date


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/urls/<int:id>/checks", methods=["POST"])
def create_check(id):
    url = get_url_by_id(id)

    if url:
        result = fetch_and_parse_url(url)
        if "error" not in result:
            insert_url_check(id, result)
            flash("Страница успешно проверена", "success")
        else:
            flash(result["error"], "danger")
    else:
        flash("URL не найден", "danger")

    return redirect(url_for("url_details", id=id))


@app.route("/urls")
def urls():
    urls_data = get_all_urls()
    return render_template("urls.html", urls=urls_data)


@app.route("/urls/<int:id>")
def url_details(id):
    url_data, checks = get_url_details(id)
    return render_template("url.html", url=url_data, checks=checks)


@app.route("/", methods=["POST"])
def add_url():
    url_input = request.form.get("url", "").strip()

    if not url_input:
        flash("URL не может быть пустым", "danger")
        return redirect(url_for("index"))
    if len(url_input) > 255:
        flash("URL слишком длинный (максимум 255 символов)", "danger")
        return redirect(url_for("index"))
    if not validators.url(url_input):
        flash("Некорректный URL", "danger")
        return redirect(url_for("index"))

    parsed = urlparse(url_input)
    normalized_url = parsed.scheme + "://" + parsed.netloc + parsed.path

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Сначала проверяем, существует ли URL
        cur.execute("SELECT id FROM urls WHERE name = %s", (normalized_url,))
        existing = cur.fetchone()

        if existing:
            url_id = existing["id"]
            flash("Такой URL уже существует", "warning")
        else:
            # Создаем новый URL с RETURNING id
            cur.execute(
                "INSERT INTO urls (name) VALUES (%s) RETURNING id",
                (normalized_url,),
            )
            print(normalized_url)
            url_id = cur.fetchone()["id"]
            conn.commit()
            flash("Страница успешно добавлена", "success")

        conn.close()
        return redirect(url_for("url_details", id=url_id))

    except Exception as e:
        conn.rollback()
        conn.close()
        flash("Произошла ошибка при добавлении", "danger")
        print(f"Error adding URL: {e}")
        return redirect(url_for("index"))
