"""Structured logging setup for the application."""

import logging
import sys

from app.config import get_settings


class FlushStreamHandler(logging.StreamHandler):
    """Handler that flushes after every emit so logs appear immediately."""

    def emit(self, record):
        super().emit(record)
        self.flush()


def setup_logger(name: str = "narration") -> logging.Logger:
    settings = get_settings()

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    if not logger.handlers:
        handler = FlushStreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logger()
