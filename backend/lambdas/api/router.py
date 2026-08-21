import json
from common.exceptions import APPError
from common.responses import api_response
from context import get_cognito_jwt_sub, get_http_method, get_path
from services import (
    generate_upload_url,
    get_moderation_result,
    get_moderation_result_view_url,
    get_moderation_results,
)
from validation import parse_last_evaluated_key, parse_limit


def _extract_image_id(path: str, suffix: str = "") -> str | None:
    if not path.startswith("/images/"):
        return None

    image_id = path.removeprefix("/images/")

    if suffix and not image_id.endswith(suffix):
        return None

    if suffix:
        image_id = image_id.removesuffix(suffix)

    return image_id or None


def route_request(event):
    method = get_http_method(event)
    path = get_path(event)

    # GET /health
    if method == "GET" and path == "/health":

        return api_response(200, {"status": "ok"})

    # POST /uploads
    if method == "POST" and path == "/uploads":

        if "body" not in event:

            raise APPError("MISSING_REQUEST_BODY", "Missing request body", 400)

        body = json.loads(event["body"])
        user_id = get_cognito_jwt_sub(event)

        return generate_upload_url(body, user_id)

    # GET /images/{id}/view-url
    if method == "GET":
        image_id = _extract_image_id(path, "/view-url")
        if image_id:
            return get_moderation_result_view_url(image_id)

        # GET /images/{id}
        image_id = _extract_image_id(path)
        if image_id:
            return get_moderation_result(image_id)

    # GET /images
    if method == "GET" and path == "/images":

        params = event.get("queryStringParameters") or {}
        limit = parse_limit(params)
        last_evaluated_key = parse_last_evaluated_key(params)

        return get_moderation_results(limit, last_evaluated_key)

    raise APPError("ROUTE_NOT_FOUND", "Route not found", 404)
