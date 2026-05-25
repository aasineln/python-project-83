from flask import Flask

from app.config import get_config
from app.routes import register_blueprints
from app.utils import format_date


def create_app(config=None):
    app = Flask(__name__)

    if config is None:
        config = get_config()

    app.config.from_object(config)
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = "dev-key-for-testing-only"

    app.jinja_env.filters["date"] = format_date
    register_blueprints(app)

    return app
