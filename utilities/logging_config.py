import logging
from pathlib import Path


def configure_logging():
    log_dir = Path(__file__).resolve().parents[1] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "automation.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
