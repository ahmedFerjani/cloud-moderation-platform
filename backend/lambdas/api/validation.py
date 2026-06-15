import json

from common.exceptions import APPError
from constants import ALLOWED_CONTENT_TYPES, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, MAX_UPLOAD_FILES


def normalize_content_types(body: dict) -> list[str]:
    content_type = body.get("content_type")

    if content_type is None:
        raise APPError("MISSING_CONTENT_TYPE", "Missing content_type", 400)

    if isinstance(content_type, str):
        content_types = [content_type]
    elif isinstance(content_type, list):
        content_types = content_type
    else:
        raise APPError(
            "INVALID_CONTENT_TYPE",
            "content_type must be a string or an array of strings",
            400,
        )

    if len(content_types) == 0:
        raise APPError("MISSING_CONTENT_TYPE", "Missing content_type", 400)

    if len(content_types) > MAX_UPLOAD_FILES:
        raise APPError(
            "TOO_MANY_FILES",
            f"A maximum of {MAX_UPLOAD_FILES} files can be uploaded per request",
            422,
        )

    for normalized_content_type in content_types:
        if not isinstance(normalized_content_type, str):
            raise APPError(
                "INVALID_CONTENT_TYPE",
                "content_type must be a string or an array of strings",
                400,
            )

        if normalized_content_type not in ALLOWED_CONTENT_TYPES:
            raise APPError("UNSUPPORTED_CONTENT_TYPE", "Unsupported content type", 415)

    return content_types


def parse_limit(params: dict) -> int:
    try:
        limit = int(params.get("limit") or DEFAULT_PAGE_SIZE)
    except ValueError:
        raise APPError("INVALID_LIMIT", "Limit must be a valid integer", 400)

    if limit <= 0:
        raise APPError("INVALID_LIMIT", "Limit must be greater than 0", 400)

    return min(limit, MAX_PAGE_SIZE)


def parse_last_evaluated_key(params: dict) -> dict[str, str] | None:
    raw_value = params.get("last_evaluated_key")

    if not raw_value:
        return None

    try:
        parsed = json.loads(raw_value)
    except (TypeError, json.JSONDecodeError):
        raise APPError(
            "INVALID_LAST_EVALUATED_KEY",
            "last_evaluated_key must be a valid JSON object",
            400,
        )

    if not isinstance(parsed, dict):
        raise APPError(
            "INVALID_LAST_EVALUATED_KEY",
            "last_evaluated_key must be a valid JSON object",
            400,
        )

    if not all(isinstance(key, str) and isinstance(value, str) for key, value in parsed.items()):
        raise APPError(
            "INVALID_LAST_EVALUATED_KEY",
            "last_evaluated_key must contain only string keys and values",
            400,
        )

    return parsed
