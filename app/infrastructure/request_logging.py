
import json
import logging
import os
import sys
from contextvars import ContextVar
from datetime import UTC, datetime

request_id_context: ContextVar[str] = ContextVar(
    "request_id",
    default="-",
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(
                record.created,
                tz=UTC,
            ).isoformat(),
            "level": record.levelname,
            "service": "pdf-storage-service",
            "request_id": getattr(
                record,
                "request_id",
                request_id_context.get(),
            ),
            "event": record.getMessage(),
        }

        for field in (
            "method",
            "path",
            "status_code",
            "duration_ms",
            "error_type",
        ):
            if hasattr(record, field):
                payload[field] = getattr(record, field)

        return json.dumps(payload, ensure_ascii=False)


def configure_logger() -> logging.Logger:
    logger = logging.getLogger("pdf_storage")
    logger.setLevel(
        os.getenv("LOG_LEVEL", "INFO").upper()
    )
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    return logger
