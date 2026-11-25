from datetime import date
from pathlib import Path

from flask import Flask

from config.settings import Settings
from database.db_utils import initialize_database


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Settings)
    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    initialize_database(app.config["DATABASE_URL"])

    from application.routes import register_routes

    register_routes(app)

    @app.context_processor
    def inject_template_globals():
        return {"current_year": date.today().year}

    return app
