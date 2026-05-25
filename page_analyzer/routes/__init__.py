from flask import Flask


def register_blueprints(app: Flask):
    from page_analyzer.routes.checks import checks_bp
    from page_analyzer.routes.main import main_bp
    from page_analyzer.routes.urls import urls_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(urls_bp)
    app.register_blueprint(checks_bp)
