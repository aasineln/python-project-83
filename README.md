### Hexlet tests and linter status:
[![Actions Status](https://github.com/aasineln/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/aasineln/python-project-83/actions)

## Project: Page Analyzer

A simple web application for adding URLs and performing basic health checks on them.

### ⚙️ How It Works

    1. Adding a URL: A user submits a URL on the main page (/). The application validates the input, normalizes it, and saves it to the urls table in the database.
    2. Viewing URLs: Users can navigate to /urls to see a list of all submitted URLs, their creation date, and the status code of the last check.
    3. Running a Check: On a specific URL's page (/urls/<id>), a user can click a "Run Check" button.
    4. Performing the Check: The server sends an HTTP request to the URL using the requests library. 
        - If the request is successful (status code 2xx), it parses the HTML to extract the <title>, <h1>, and meta description.
        - If the request fails (network error, timeout, or status code 4xx/5xx), no new check record is created, and a flash message is shown to the user. 
    5. Storing Results: The results of a successful check (status code, title, etc.) are saved in the url_checks table, linked to the original URL. 
    6. Displaying Results: The user is redirected back to the URL's page, where they can see the history of all checks performed.

### 🚀 Getting Started

This project is a Flask-based web service that allows users to submit website URLs, store them in a PostgreSQL database, and run checks to gather information like HTTP status codes, titles, and meta descriptions.
Prerequisites
To run this project locally, you need to have the following installed:
  Python 3.8+
  PostgreSQL (A running database server)
  pipenv or venv for managing virtual environments (recommended)
  GNU Make (for running build and start commands)

### 📦 Installing

1. Clone the repository:
```bash
    git clone https://github.com/aasineln/python-project-83.git
    cd python-project-83
```

2. Create and activate a virtual environment:
```bash
    python -m venv .venv
    source .venv/bin/activate # On Windows use .venv\Scripts\activate
```

3. Install dependencies:The project uses uv for fast dependency management.
```bash
  make install
```

4. Configure Database
Set up the database:
- Create a new database in your PostgreSQL instance (e.g., page_analyzer_dev).
- Create a .env file in the root directory with your database connection string:
```bash
  DATABASE_URL=postgres://username:password@localhost:5432/page_analyzer_dev
```
- Run the build script to create tables and run migrations:
```bash
    make build
```

5. Run the application:
```bash
  make start
```
The application will be available at http://127.0.0.1:5000.


### ✅ Technology Stack

    Backend: Python 3, Flask web framework.
    Database: PostgreSQL.
    Database Driver: psycopg.
    HTML Templating: Jinja2.
    HTTP Requests: requests.
    HTML Parsing: BeautifulSoup4 (bs4).
    Environment Management: python-dotenv.
    Frontend Styling: Bootstrap 5 (via CDN).
    Package Management: uv / pip.
    Build Tooling: GNU Make.

🛠️ Commands

    make install: Install Python dependencies.
    make build: Run database migrations (creates tables).
    make start: Start the Flask development server.
    make lint: Check code style with a linter 