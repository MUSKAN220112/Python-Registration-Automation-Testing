# Registration Form Automation Framework

A beginner-friendly portfolio project containing a Flask registration site, a configurable SQLite/MySQL database, API checks, and Selenium Page Object Model tests.

## What is included

- **Flask website and API**: `/` and `/login` serve the Automation Workspace landing page, which includes the account sign-in form and workspace features. `/dashboard` shows protected project and test-report data. `/register` creates accounts, `/api/register` provides JSON registration, and `/health` is a small health check.
- **Database**: SQLAlchemy creates the `users` table. SQLite works out of the box; set `DATABASE_URL` to use MySQL. Passwords are stored only as Werkzeug password hashes and are checked during login.
- **Automated tests**: pytest checks form rules, CSV/Excel data-driven cases, HTTP API behavior through Requests, database persistence, and optional Selenium browser journeys.
- **Reports and CI**: pytest HTML and Allure result files go under `reports/`; GitHub Actions and Jenkins run the suite.

## Quick start (Windows PowerShell)

Run these commands from this project folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pytest
```

If PowerShell blocks activation, enable it for this terminal only with
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again.
If Python 3.12 is not installed, use another supported Python 3.11+ interpreter
when creating the virtual environment.

The default test command runs the app, API, database, and CSV/Excel tests without
requiring a browser or MySQL server. The data-driven suite reads the 50 supplied
records from each file in `test_data\` (100 cases total). Both formats are read
directly; routine test runs do not regenerate or overwrite the input files.
Test databases are isolated SQLite files and do not touch application data.

## Run the website

```powershell
python run.py
```

Visit `http://127.0.0.1:5000` for the landing page and sign-in form, or open
`http://127.0.0.1:5000/register` to create an account. Successful sign-in
redirects to the protected `http://127.0.0.1:5000/dashboard` page; opening that
URL without a valid session redirects to login. Logout also returns to login.
Landing-page metrics and dashboard test-case rows come from the saved
`reports\pytest-report.html`; test execution totals and recent executions are
read from valid result records in `reports\allure-results\`. The landing page
does not offer self-service password reset; account assistance is directed to
the platform administrator. The default database is
`instance\registration.db`, created automatically on first startup.

## MySQL setup (optional)

1. Install and start MySQL Server.
2. Connect to MySQL and run `database\schema.sql` (or create a database named
   `registration_db`; SQLAlchemy creates the table when the app starts).
3. Copy `.env.example` to `.env` and set `DATABASE_URL` to a URL for a dedicated
   application account, for example:

   ```text
   DATABASE_URL=mysql+pymysql://registration_user:your-password@localhost:3306/registration_db?charset=utf8mb4
   ```

4. Install `python-dotenv` (already in requirements) and export the values before
   launching if desired. The app deliberately does not load `.env` implicitly:
   PowerShell can load it for the current session like this:

   ```powershell
   $env:DATABASE_URL = "mysql+pymysql://registration_user:your-password@localhost:3306/registration_db?charset=utf8mb4"
   $env:SECRET_KEY = "use-a-long-random-value-here"
   python run.py
   ```

Never commit `.env` or use an administrator MySQL account in a deployed app. If
MySQL is unavailable, the default SQLite mode still supports the full test suite.

## Selenium browser tests

Selenium tests use headless Chrome by default. Selenium Manager may download a
matching browser driver when needed; install Chrome (or Firefox) first and allow
driver downloads/network access. Run:

```powershell
python -m pytest -m ui
$env:BROWSER = "firefox"
python -m pytest -m ui
```

The `driver` fixture uses explicit waits and supports `chrome` and `firefox`.
Failed browser tests save screenshots under `screenshots\` and attach them to
Allure results when the plugin is available.

## Reports, parallel runs, and useful commands

```powershell
python -m pytest -n 2
python -m pytest -m ui
python -m pytest --html=reports\pytest-report.html --self-contained-html
allure serve reports\allure-results
```

The pytest HTML report shows passed/failed/skipped counts, elapsed time, and
failure details. Allure's result files are generated automatically; the `allure`
command-line application is needed to render an interactive Allure site.
The framework writes logs to `logs\automation.log`.

## Beginner architecture guide

1. `application\` contains the Flask app factory, authenticated routes,
   templates, and shared/static page styling.
2. `database\` defines the users table and database operations, including
   password-hash lookups for login.
3. `utilities\validation.py` is the single source for server-side form rules;
   `utilities\dashboard_data.py` reads actual project and report data.
4. `test_data\registration_data.csv` and `test_data\registration_data.xlsx`
   provide the CSV and Excel inputs. `utilities\generate_test_data.py` is an
   optional synthetic-data generator that overwrites these files if run.
5. `tests\` covers the generated data, database behavior, validation boundaries,
   and Selenium page behavior. `api_tests\` checks the HTTP API using Requests.
6. `pages\registration_page.py` wraps Selenium interactions in a Page Object.
7. `conftest.py` provides isolated test databases, test servers, browsers, and
   failure screenshots.
8. `.github\workflows\` and `Jenkinsfile` automate test execution and artifact
   collection. `Dockerfile` packages the Flask app.

Use GitHub by running `git init`, reviewing `.gitignore`, then adding a remote
and pushing your branch. Do not commit credentials or the local SQLite database.
