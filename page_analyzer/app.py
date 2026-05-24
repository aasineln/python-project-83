import os
from urllib.parse import urlparse

import psycopg
import validators
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from psycopg.rows import dict_row

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
app = Flask(__name__)
app.secret_key = "ваш_секретный_ключ_для_flash"


def get_db_connection():
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    return conn


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/urls", methods=["GET"])
def list_urls():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, created_at FROM urls ORDER BY created_at DESC"
    )
    urls = cur.fetchall()
    conn.close()
    return render_template("urls.html", urls=urls)


@app.route("/urls/<int:id>", methods=["GET"])
def show_url(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, created_at FROM urls WHERE id = %s", (id,))
    url = cur.fetchone()
    conn.close()
    if url is None:
        flash("Запись не найдена", "danger")
        return redirect(url_for("list_urls"))
    return render_template("url.html", url=url)


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

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO urls (name) VALUES (%s)", (normalized_url,))
        conn.commit()
        flash("URL успешно добавлен", "success")
    except psycopg.errors.UniqueViolation:
        flash("Такой URL уже существует", "warning")
    except Exception as e:
        flash("Произошла ошибка при добавлении", "danger")
        print(e)  # Для логов
    finally:
        if "conn" in locals():
            conn.close()

    return redirect(url_for("index"))
