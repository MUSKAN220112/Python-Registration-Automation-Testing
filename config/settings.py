import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "local-development-key-change-me")
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{PROJECT_ROOT / 'instance' / 'registration.db'}",
    )
    TESTING = False
