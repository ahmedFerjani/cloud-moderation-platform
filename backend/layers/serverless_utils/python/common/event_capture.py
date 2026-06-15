"""Ingress event capture utilities for Lambda handlers.

When CAPTURE_SAMPLE_EVENTS is enabled, incoming events are sanitized to redact
sensitive and volatile metadata. In AWS, sanitized payloads are logged to
CloudWatch. In local SAM runs, sanitized payloads are written to fixture files
under events/captured for replay and tests.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common.logger import log

REDACTED_VALUE = "<redacted>"
TRUNCATED_VALUE = "<truncated>"
MAX_CAPTURED_EVENT_CHARS = 12000
LOCAL_CAPTURE_DIR = "events/captured"
TRUTHY_VALUES = frozenset({"1", "true", "yes", "on"})
SENSITIVE_KEYWORDS = {
    "authorization",
    "credentials",
    "password",
    "principalid",
    "receipthandle",
    "secret",
    "senderid",
    "signature",
    "token",
    "x-amz-id-2",
    "x-amz-request-id",
    "x-amz-security-token",
    "x-amz-signature",
    "x-api-key",
}
VOLATILE_METADATA_KEYWORDS = {
    "apiid",
    "approximatefirstreceivetimestamp",
    "approximatereceivetimestamp",
    "host",
    "domainname",
    "domainprefix",
    "eventtime",
    "messageid",
    "requestid",
    "senttimestamp",
    "sourceip",
    "user-agent",
    "useragent",
    "time",
    "timeepoch",
    "x-amzn-trace-id",
    "x-forwarded-for",
}
AWS_ACCOUNT_ID_PATTERN = re.compile(r"\b\d{12}\b")


def _is_enabled() -> bool:

    return os.getenv("CAPTURE_SAMPLE_EVENTS", "false").strip().lower() in TRUTHY_VALUES


def _is_sam_local() -> bool:

    return os.getenv("AWS_SAM_LOCAL", "false").strip().lower() in TRUTHY_VALUES


def _should_redact(key: str) -> bool:

    normalized = key.strip().lower()

    # Redact secrets and volatile metadata fields.
    return any(keyword in normalized for keyword in SENSITIVE_KEYWORDS) or any(
        keyword in normalized for keyword in VOLATILE_METADATA_KEYWORDS
    )


def _parse_json_string(value: str) -> Any | None:

    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return None


def _sanitize(value: Any, key_name: str = "") -> Any:

    if key_name and _should_redact(key_name):
        return REDACTED_VALUE

    # Redact sensitive data in nested fields.
    if isinstance(value, dict):
        sanitized = {}

        for key, item in value.items():
            sanitized[key] = _sanitize(item, str(key))

        return sanitized

    if isinstance(value, list):
        return [_sanitize(item) for item in value]

    if key_name == "body" and isinstance(value, str):
        parsed_body = _parse_json_string(value)
        if parsed_body is not None:
            return _sanitize(parsed_body)

    if isinstance(value, bytes):
        return TRUNCATED_VALUE

    if isinstance(value, str) and len(value) > 2000:
        value = f"{value[:2000]}{TRUNCATED_VALUE}"

    if isinstance(value, str):
        # Mask embedded account IDs in free-form strings like ARNs and bucket names.
        return AWS_ACCOUNT_ID_PATTERN.sub(REDACTED_VALUE, value)

    return value


def _save_event_to_file(lambda_name: str, event: Any, request_id: str) -> str:

    output_dir = os.getenv("CAPTURE_EVENTS_OUTPUT_DIR", LOCAL_CAPTURE_DIR)
    capture_dir = Path(output_dir)
    capture_dir.mkdir(parents=True, exist_ok=True)

    # Use UTC time and request IDs so each file is unique.
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_lambda_name = lambda_name.replace("/", "-").replace(" ", "-")
    safe_request_id = request_id.replace("/", "-")
    file_path = capture_dir / f"{safe_lambda_name}-{timestamp}-{safe_request_id}.json"

    with file_path.open("w", encoding="utf-8") as output_file:
        json.dump(event, output_file, indent=2, sort_keys=True, default=str)

    return str(file_path)


def capture_sample_event(lambda_name: str, event: dict[str, Any], context: Any) -> None:

    if not _is_enabled():
        return

    request_id = getattr(context, "aws_request_id", "unknown")
    sanitized_event = _sanitize(event)

    if _is_sam_local():
        # Local SAM saves a fixture file for replay.
        file_path = _save_event_to_file(lambda_name, sanitized_event, request_id)
        log(
            "INFO",
            "Captured sample ingress event to file",
            {
                "lambda_name": lambda_name,
                "aws_request_id": request_id,
                "event_file_path": file_path,
            },
        )
        return

    estimated_payload_size = len(str(sanitized_event))
    is_truncated = 0
    event_payload: Any = sanitized_event

    if estimated_payload_size > MAX_CAPTURED_EVENT_CHARS:
        is_truncated = 1
        event_payload = f"{str(sanitized_event)[:MAX_CAPTURED_EVENT_CHARS]}{TRUNCATED_VALUE}"

    # In AWS, capture the event in logs instead of writing a file.
    log(
        "INFO",
        "Captured sample ingress event",
        {
            "lambda_name": lambda_name,
            "aws_request_id": request_id,
            "event_payload": event_payload,
            "event_truncated": is_truncated,
        },
    )
