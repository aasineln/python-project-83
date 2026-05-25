from flask import Flask

from page_analyzer.config import get_config
from page_analyzer.routes import register_blueprints
from page_analyzer.utils import format_date


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


app = create_app()
