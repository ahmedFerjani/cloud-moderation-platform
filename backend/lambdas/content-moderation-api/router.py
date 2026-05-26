import json
from common.exceptions import APPError
from services import (
    generate_upload_url,
    get_moderation_result,
    get_moderation_results,
    parse_limit,
)


def route_request(event):
    method = event["requestContext"]["http"]["method"]
    path = event["rawPath"]

    # POST /generate-upload-url
    if method == "POST" and path == "/generate-upload-url":

        if "body" not in event:

            raise APPError("MISSING_REQUEST_BODY", "Missing request body", 400)

        body = json.loads(event["body"])

        return generate_upload_url(body)

    # GET /moderation-results/{imageId}
    if method == "GET" and path.startswith("/moderation-results/"):

        image_id = path.split("/moderation-results/")[1]

        return get_moderation_result(image_id)

    # GET /moderation-results
    if method == "GET" and path == "/moderation-results":

        params = event.get("queryStringParameters") or {}
        limit = parse_limit(params)

        return get_moderation_results(limit)

    raise APPError("ROUTE_NOT_FOUND", "Route not found", 404)
