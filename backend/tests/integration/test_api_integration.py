import json
from typing import Any, cast
from botocore.exceptions import ClientError
from unittest.mock import patch

from _integration_test_setup import (
    FakeS3Client,
    FakeTable,
    api_runtime_event,
    load_api_stack,
    runtime_context,
)


def assert_api_headers(response: dict) -> None:
    assert response["headers"]["Content-Type"] == "application/json"
    assert response["headers"]["Access-Control-Allow-Origin"] == "*"


def assert_api_error(response: dict, status_code: int, code: str, message: str) -> None:
    body = json.loads(response["body"])
    assert response["statusCode"] == status_code
    assert_api_headers(response)
    assert body["error"]["code"] == code
    assert body["error"]["message"] == message


# Verifies the health route returns a successful operational status payload.
def test_api_handler_routes_get_health_end_to_end() -> None:
    _api_services, _api_router, api_handler = load_api_stack()
    event = api_runtime_event("api-images.json")
    event["requestContext"]["http"]["method"] = "GET"
    event["rawPath"] = "/health"

    with patch.object(api_handler, "capture_sample_event"):
        response = api_handler.lambda_handler(event, runtime_context("req-health"))

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert_api_headers(response)
    assert body == {"status": "ok"}


# Verifies the upload URL route returns the full presigned POST contract.
def test_api_handler_routes_generate_upload_url_end_to_end() -> None:
    api_services, _api_router, api_handler = load_api_stack()
    service_module = cast(Any, api_services)
    fake_s3 = FakeS3Client()
    service_module.s3 = fake_s3

    event = api_runtime_event("api-uploads.json")
    context = runtime_context("req-api")

    with patch.object(api_handler, "capture_sample_event"):
        response = api_handler.lambda_handler(event, context)

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert_api_headers(response)
    assert body["count"] == 1
    assert body["uploads"][0]["upload_url"] == "https://example-upload.test"
    assert body["uploads"][0]["upload_method"] == "POST"
    assert body["uploads"][0]["upload_form_fields"]["Content-Type"] == "image/jpeg"
    assert body["uploads"][0]["object_key"] == body["uploads"][0]["upload_form_fields"]["key"]
    assert body["uploads"][0]["object_key"].startswith("uploads/")
    assert body["uploads"][0]["object_key"].endswith(".jpg")
    assert body["max_upload_size_bytes"] == service_module.MAX_UPLOAD_FILE_SIZE_BYTES
    assert body["expires_in"] == service_module.UPLOAD_URL_EXPIRES_IN_SECONDS
    assert len(fake_s3.presigned_posts) == 1


# Verifies the upload URL route returns a presigned payload per file when content_type is a list.
def test_api_handler_routes_generate_upload_url_multifile_end_to_end() -> None:
    api_services, _api_router, api_handler = load_api_stack()
    service_module = cast(Any, api_services)
    fake_s3 = FakeS3Client()
    service_module.s3 = fake_s3

    event = api_runtime_event("api-uploads.json")
    event["body"] = json.dumps({"content_type": ["image/jpeg", "image/png"]})

    with patch.object(api_handler, "capture_sample_event"):
        response = api_handler.lambda_handler(event, runtime_context("req-api-multifile"))

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert_api_headers(response)
    assert body["count"] == 2
    assert len(body["uploads"]) == 2
    assert body["uploads"][0]["content_type"] == "image/jpeg"
    assert body["uploads"][1]["content_type"] == "image/png"
    assert body["max_upload_size_bytes"] == service_module.MAX_UPLOAD_FILE_SIZE_BYTES
    assert len(fake_s3.presigned_posts) == 2


# Verifies the single-result route returns the stored moderation record by image ID.
def test_api_handler_routes_get_moderation_result_end_to_end() -> None:
    api_services, _api_router, api_handler = load_api_stack()
    service_module = cast(Any, api_services)
    service_module.table = FakeTable(
        items=[
            {
                "image_id": "00000000-0000-0000-0000-000000000000",
                "status": "safe",
                "s3_key": "uploads/00000000-0000-0000-0000-000000000000.jpg",
            }
        ]
    )

    event = api_runtime_event("api-image-by-id.json")

    with patch.object(api_handler, "capture_sample_event"):
        response = api_handler.lambda_handler(event, runtime_context("req-get-one"))

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert_api_headers(response)
    assert body["image_id"] == "00000000-0000-0000-0000-000000000000"
    assert body["status"] == "safe"


# Verifies the list route applies the requested limit and returns collection metadata.
def test_api_handler_routes_list_moderation_results_end_to_end() -> None:
    api_services, _api_router, api_handler = load_api_stack()
    service_module = cast(Any, api_services)
    service_module.table = FakeTable(
        items=[
            {"image_id": "img-1", "status": "safe", "s3_key": "uploads/img-1.jpg"},
            {"image_id": "img-2", "status": "flagged", "s3_key": "uploads/img-2.png"},
        ]
    )

    event = api_runtime_event("api-images.json")
    event["queryStringParameters"] = {"limit": "1"}

    with patch.object(api_handler, "capture_sample_event"):
        response = api_handler.lambda_handler(event, runtime_context("req-list"))

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert_api_headers(response)
    assert body["count"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["image_id"] == "img-1"
    assert body["last_evaluated_key"] is None


# Verifies malformed request bodies are normalized into the public invalid-JSON error contract.
def test_api_handler_returns_invalid_json_error_contract() -> None:
    _api_services, _api_router, api_handler = load_api_stack()
    event = api_runtime_event("api-uploads.json")
    event["body"] = "{bad-json"

    with patch.object(api_handler, "capture_sample_event"):
        response = api_handler.lambda_handler(event, runtime_context("req-invalid-json"))

    assert_api_error(response, 400, "INVALID_JSON", "Invalid JSON request body")


# Verifies unsupported upload content types are rejected with the expected API error payload.
def test_api_handler_returns_unsupported_content_type_error_contract() -> None:
    _api_services, _api_router, api_handler = load_api_stack()
    event = api_runtime_event("api-uploads.json")
    event["body"] = json.dumps({"content_type": "image/gif"})

    with patch.object(api_handler, "capture_sample_event"):
        response = api_handler.lambda_handler(
            event, runtime_context("req-unsupported-content-type")
        )

    assert_api_error(
        response,
        415,
        "UNSUPPORTED_CONTENT_TYPE",
        "Unsupported content type",
    )


# Verifies too-many-files payloads are rejected with an unprocessable-entity contract.
def test_api_handler_returns_too_many_files_error_contract() -> None:
    _api_services, _api_router, api_handler = load_api_stack()
    event = api_runtime_event("api-uploads.json")
    event["body"] = json.dumps({"content_type": ["image/jpeg"] * 11})

    with patch.object(api_handler, "capture_sample_event"):
        response = api_handler.lambda_handler(event, runtime_context("req-too-many-files"))

    assert_api_error(
        response,
        422,
        "TOO_MANY_FILES",
        "A maximum of 10 files can be uploaded per request",
    )


# Verifies missing moderation records surface as the public not-found API contract.
def test_api_handler_returns_not_found_error_contract() -> None:
    api_services, _api_router, api_handler = load_api_stack()
    service_module = cast(Any, api_services)
    service_module.table = FakeTable(items=[])
    event = api_runtime_event("api-image-by-id.json")

    with patch.object(api_handler, "capture_sample_event"):
        response = api_handler.lambda_handler(event, runtime_context("req-not-found"))

    assert_api_error(
        response,
        404,
        "MODERATION_RESULT_NOT_FOUND",
        "Moderation result not found",
    )


# Verifies invalid pagination input is rejected with the expected validation error contract.
def test_api_handler_returns_invalid_limit_error_contract() -> None:
    _api_services, _api_router, api_handler = load_api_stack()
    event = api_runtime_event("api-images.json")
    event["queryStringParameters"] = {"limit": "invalid"}

    with patch.object(api_handler, "capture_sample_event"):
        response = api_handler.lambda_handler(event, runtime_context("req-invalid-limit"))

    assert_api_error(response, 400, "INVALID_LIMIT", "Limit must be a valid integer")


# Verifies unmatched routes are normalized into the public route-not-found error contract.
def test_api_handler_returns_route_not_found_error_contract() -> None:
    _api_services, _api_router, api_handler = load_api_stack()
    event = api_runtime_event("api-images.json")
    event["rawPath"] = "/unknown-route"
    event["requestContext"]["http"]["path"] = "/unknown-route"
    event["requestContext"]["http"]["method"] = "POST"

    with patch.object(api_handler, "capture_sample_event"):
        response = api_handler.lambda_handler(event, runtime_context("req-route-not-found"))

    assert_api_error(response, 404, "ROUTE_NOT_FOUND", "Route not found")


# Verifies upstream AWS client failures are translated into the generic service error contract.
def test_api_handler_returns_aws_service_error_contract() -> None:
    api_services, _api_router, api_handler = load_api_stack()
    service_module = cast(Any, api_services)
    fake_s3 = FakeS3Client()
    service_module.s3 = fake_s3
    event = api_runtime_event("api-uploads.json")
    aws_error = ClientError(
        error_response={
            "Error": {"Code": "InternalError", "Message": "simulated upstream failure"}
        },
        operation_name="GeneratePresignedPost",
    )

    with patch.object(fake_s3, "generate_presigned_post", side_effect=aws_error):
        with patch.object(api_handler, "capture_sample_event"):
            response = api_handler.lambda_handler(event, runtime_context("req-aws-error"))

    assert_api_error(
        response,
        500,
        "AWS_SERVICE_ERROR",
        "A cloud service error occurred",
    )
