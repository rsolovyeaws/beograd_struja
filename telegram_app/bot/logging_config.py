"""Module that sets up the logger for the application."""

import logging


def setup_logger() -> None:
    """Set up the logger for the application."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # Reduce verbosity for external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)

    file_handler = logging.FileHandler("./logs/beograd_strujia_app.log")
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
