import json
import logging
import sys
from app.core.config import settings

# Keys to redact in log messages (case-insensitive substring match)
_SECRET_SUBSTRINGS = (
    "api_key", "apikey", "secret", "password", "token", "authorization",
    "openai", "anthropic", "stripe", "bearer ",
)


class SecretsRedactionFilter(logging.Filter):
    """Redact secret-like values in log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if hasattr(record, "msg") and isinstance(record.msg, str):
            msg = record.msg
            for sub in _SECRET_SUBSTRINGS:
                if sub.lower() in msg.lower():
                    # Replace potential key=value or "key": "value" patterns with redacted
                    record.msg = "[REDACTED]"
                    break
        return True


class RequestIDFilter(logging.Filter):
    """Add request_id to log record if set (from middleware context)."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            from app.core.middleware import request_id_ctx
            rid = request_id_ctx.get()
            record.request_id = rid or ""
        except Exception:
            record.request_id = ""
        return True


class JsonFormatter(logging.Formatter):
    """JSON log format for production (log aggregators)."""

    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if getattr(record, "request_id", None):
            log["request_id"] = record.request_id
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        return json.dumps(log)


def setup_logging():
    """Configure logging for the application."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    is_production = getattr(settings, "ENVIRONMENT", "").lower() == "production"

    # Filters (request_id first so formatter can use it)
    request_id_filter = RequestIDFilter()
    secrets_filter = SecretsRedactionFilter()

    if is_production:
        formatter = JsonFormatter(datefmt="%Y-%m-%dT%H:%M:%S")
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(request_id)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.addFilter(request_id_filter)
    console_handler.addFilter(secrets_filter)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
