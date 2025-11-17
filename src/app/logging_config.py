import logging
import sys
from contextvars import ContextVar
from logging.config import dictConfig

from .config import get_settings

request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
        record.request_id = request_id_ctx_var.get("-")
        return True


def configure_logging() -> None:
    settings = get_settings()
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {"request_id": {"()": RequestIdFilter}},
            "formatters": {
                "default": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s request_id=%(request_id)s %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": sys.stdout,
                    "filters": ["request_id"],
                }
            },
            "loggers": {
                "uvicorn.error": {"handlers": ["console"], "level": settings.log_level},
                "uvicorn.access": {"handlers": ["console"], "level": settings.log_level},
                "app": {
                    "handlers": ["console"],
                    "level": settings.log_level,
                    "propagate": False,
                },
            },
            "root": {"handlers": ["console"], "level": settings.log_level},
        }
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
