"""Lightweight structured JSON logger for Lambda functions."""

import json
from typing import Any


def log(level: str, message: str, extra: dict[str, Any] | None = None):

    log_data: dict[str, Any] = {
        "level": level,
        "message": message,
    }

    if extra:
        log_data.update(extra)

    print(json.dumps(log_data))
