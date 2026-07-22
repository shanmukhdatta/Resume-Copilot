"""Structured application-wide logger factory."""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from app.config import get_settings

_CONFIGURED_LOGGERS: dict[str, logging.Logger] = {}


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger with console + rotating file handlers."""
    if name in _CONFIGURED_LOGGERS:
        return _CONFIGURED_LOGGERS[name]

    settings = get_settings()
    os.makedirs(settings.LOG_DIR, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)
    logger.propagate = False

    if not logger.handlers:
        fmt = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(fmt)
        logger.addHandler(console_handler)

        file_handler = RotatingFileHandler(
            os.path.join(settings.LOG_DIR, "app.log"),
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
        )
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)

    _CONFIGURED_LOGGERS[name] = logger
    return logger
