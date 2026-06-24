import json
from common.exceptions import APPError
from common.responses import api_response
from services import (
    generate_upload_url,
    get_moderation_result,
    get_moderation_results,
)
from validation import parse_last_evaluated_key, parse_limit


def route_request(event):
    method = event["requestContext"]["http"]["method"]
    path = event["rawPath"]

    # GET /health
    if method == "GET" and path == "/health":

        return api_response(200, {"status": "ok"})

    # POST /uploads
    if method == "POST" and path == "/uploads":

        if "body" not in event:

            raise APPError("MISSING_REQUEST_BODY", "Missing request body", 400)

        body = json.loads(event["body"])

        return generate_upload_url(body)

    # GET /images/{id}
    if method == "GET" and path.startswith("/images/"):

        image_id = path.split("/images/")[1]

        return get_moderation_result(image_id)

    # GET /images
    if method == "GET" and path == "/images":

        params = event.get("queryStringParameters") or {}
        limit = parse_limit(params)
        last_evaluated_key = parse_last_evaluated_key(params)

        return get_moderation_results(limit, last_evaluated_key)

    raise APPError("ROUTE_NOT_FOUND", "Route not found", 404)
