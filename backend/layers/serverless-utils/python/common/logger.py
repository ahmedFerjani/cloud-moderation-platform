"""Lightweight structured JSON logger for Lambda functions."""

import json
from decimal import Decimal
from typing import Any


def _json_default(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    return str(value)


def log(level: str, message: str, extra: dict[str, Any] | None = None):

    log_data: dict[str, Any] = {
        "level": level,
        "message": message,
    }

    if extra:
        log_data.update(extra)

    print(json.dumps(log_data, default=_json_default))
