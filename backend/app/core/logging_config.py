"""Structured logging configuration for ATC System."""

import logging
import sys
from typing import Optional


def setup_logging(level: Optional[str] = None):
    """Configure application-wide logging."""
    log_level = getattr(logging, (level or "INFO").upper(), logging.INFO)

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=log_level,
        format=fmt,
        datefmt=date_fmt,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Silence noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info("Logging initialized at level: %s", logging.getLevelName(log_level))
