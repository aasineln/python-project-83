#!/usr/bin/env python3
"""WSGI entry point for production."""

from page_analyzer import create_app

# Create application instance
app = create_app()

# For Gunicorn
application = app

if __name__ == "__main__":
    app.run()
