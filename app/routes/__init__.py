from flask import Flask


def register_blueprints(app: Flask):
    from app.routes.checks import checks_bp
    from app.routes.main import main_bp
    from app.routes.urls import urls_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(urls_bp)
    app.register_blueprint(checks_bp)
