"""
AI Tutor Backend — Structured Logging Setup.

Uses structlog with JSON output for production-ready logging.
Every log entry is a structured JSON object, making it easy to
search and filter in production monitoring tools.
"""

import logging
import sys

import structlog

from app.config import settings


def setup_logging() -> None:
    """Configure structlog for the application.

    - Development: pretty-printed, colored console output.
    - Production: JSON lines for log aggregation.
    """
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if settings.is_development:
        # Pretty console output for development
        renderer: structlog.types.Processor = structlog.dev.ConsoleRenderer()
    else:
        # JSON output for production log aggregation
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure the standard library root logger to use structlog's formatter
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a named structured logger.

    Usage:
        logger = get_logger(__name__)
        logger.info("something happened", key="value")
    """
    return structlog.get_logger(name)
