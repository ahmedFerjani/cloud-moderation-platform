"""HTTP response helpers shared by API Lambda handlers."""

import json
import os
from typing import Any
from common.encoders import DecimalEncoder

CORS_ORIGIN = os.getenv("CORS_ORIGIN", "*")


def api_response(status_code: int, body: dict[str, Any]) -> dict[str, Any]:

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": CORS_ORIGIN,
        },
        "body": json.dumps(body, cls=DecimalEncoder),
    }
