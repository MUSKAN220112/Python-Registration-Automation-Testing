import logging
import os
import threading

import pytest
from werkzeug.serving import make_server

from application import create_app
from utilities.logging_config import configure_logging


configure_logging()
LOGGER = logging.getLogger(__name__)


@pytest.fixture
def app(tmp_path):
    database_path = tmp_path / "test-registration.sqlite"
    application = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-key",
        "DATABASE_URL": f"sqlite:///{database_path}",
    })
    return application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def api_base_url(app):
    server = make_server("127.0.0.1", 0, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)


@pytest.fixture
def browser_name():
    return os.getenv("BROWSER", "chrome").lower()


@pytest.fixture
def driver(request, browser_name):
    from selenium import webdriver

    if browser_name == "chrome":
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        browser = webdriver.Chrome(options=options)
    elif browser_name == "firefox":
        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")
        browser = webdriver.Firefox(options=options)
    else:
        raise ValueError(f"Unsupported BROWSER value: {browser_name}")
    browser.set_window_size(1280, 900)
    yield browser
    browser.quit()


@pytest.fixture
def live_app_url(app):
    server = make_server("127.0.0.1", 0, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        browser = item.funcargs.get("driver")
        if browser:
            screenshot_dir = os.path.join("screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = os.path.abspath(
                os.path.join(screenshot_dir, f"{item.name}.png")
            )
            if browser.save_screenshot(screenshot_path):
                LOGGER.error("Saved failure screenshot to %s", screenshot_path)
                try:
                    import allure
                    allure.attach.file(screenshot_path, name=item.name,
                                       attachment_type=allure.attachment_type.PNG)
                except ImportError:
                    LOGGER.warning("Allure is not installed; screenshot saved locally.")
