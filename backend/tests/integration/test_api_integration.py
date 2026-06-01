import json
import unittest
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


class ApiIntegrationTests(unittest.TestCase):
    def assert_api_headers(self, response: dict) -> None:
        self.assertEqual(response["headers"]["Content-Type"], "application/json")
        self.assertEqual(response["headers"]["Access-Control-Allow-Origin"], "*")

    def assert_api_error(self, response: dict, status_code: int, code: str, message: str) -> None:
        body = json.loads(response["body"])
        self.assertEqual(response["statusCode"], status_code)
        self.assert_api_headers(response)
        self.assertEqual(body["error"]["code"], code)
        self.assertEqual(body["error"]["message"], message)

    # Verifies the upload URL route returns the full presigned POST contract.
    def test_api_handler_routes_generate_upload_url_end_to_end(self) -> None:
        api_services, _api_router, api_handler = load_api_stack()
        service_module = cast(Any, api_services)
        fake_s3 = FakeS3Client()
        service_module.s3 = fake_s3

        event = api_runtime_event("api-generate-upload-url.json")
        context = runtime_context("req-api")

        with patch.object(api_handler, "capture_sample_event"):
            response = api_handler.lambda_handler(event, context)

        body = json.loads(response["body"])
        self.assertEqual(response["statusCode"], 200)
        self.assert_api_headers(response)
        self.assertEqual(body["upload_url"], "https://example-upload.test")
        self.assertEqual(body["upload_method"], "POST")
        self.assertEqual(body["upload_form_fields"]["Content-Type"], "image/jpeg")
        self.assertEqual(body["object_key"], body["upload_form_fields"]["key"])
        self.assertTrue(body["object_key"].startswith("uploads/"))
        self.assertTrue(body["object_key"].endswith(".jpg"))
        self.assertEqual(body["max_upload_size_bytes"], service_module.MAX_UPLOAD_SIZE_BYTES)
        self.assertEqual(body["expires_in"], service_module.UPLOAD_URL_EXPIRES_IN_SECONDS)
        self.assertEqual(len(fake_s3.presigned_posts), 1)

    # Verifies the single-result route returns the stored moderation record by image ID.
    def test_api_handler_routes_get_moderation_result_end_to_end(self) -> None:
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

        event = api_runtime_event("api-moderation-result-by-image-id.json")

        with patch.object(api_handler, "capture_sample_event"):
            response = api_handler.lambda_handler(event, runtime_context("req-get-one"))

        body = json.loads(response["body"])
        self.assertEqual(response["statusCode"], 200)
        self.assert_api_headers(response)
        self.assertEqual(body["image_id"], "00000000-0000-0000-0000-000000000000")
        self.assertEqual(body["status"], "safe")

    # Verifies the list route applies the requested limit and returns collection metadata.
    def test_api_handler_routes_list_moderation_results_end_to_end(self) -> None:
        api_services, _api_router, api_handler = load_api_stack()
        service_module = cast(Any, api_services)
        service_module.table = FakeTable(
            items=[
                {"image_id": "img-1", "status": "safe", "s3_key": "uploads/img-1.jpg"},
                {"image_id": "img-2", "status": "flagged", "s3_key": "uploads/img-2.png"},
            ]
        )

        event = api_runtime_event("api-moderation-results.json")
        event["queryStringParameters"] = {"limit": "1"}

        with patch.object(api_handler, "capture_sample_event"):
            response = api_handler.lambda_handler(event, runtime_context("req-list"))

        body = json.loads(response["body"])
        self.assertEqual(response["statusCode"], 200)
        self.assert_api_headers(response)
        self.assertEqual(body["count"], 1)
        self.assertEqual(len(body["items"]), 1)
        self.assertEqual(body["items"][0]["image_id"], "img-1")
        self.assertIsNone(body["last_evaluated_key"])

    # Verifies malformed request bodies are normalized into the public invalid-JSON error contract.
    def test_api_handler_returns_invalid_json_error_contract(self) -> None:
        _api_services, _api_router, api_handler = load_api_stack()
        event = api_runtime_event("api-generate-upload-url.json")
        event["body"] = "{bad-json"

        with patch.object(api_handler, "capture_sample_event"):
            response = api_handler.lambda_handler(event, runtime_context("req-invalid-json"))

        self.assert_api_error(response, 400, "INVALID_JSON", "Invalid JSON request body")

    # Verifies unsupported upload content types are rejected with the expected API error payload.
    def test_api_handler_returns_unsupported_content_type_error_contract(self) -> None:
        _api_services, _api_router, api_handler = load_api_stack()
        event = api_runtime_event("api-generate-upload-url.json")
        event["body"] = json.dumps({"content_type": "image/gif"})

        with patch.object(api_handler, "capture_sample_event"):
            response = api_handler.lambda_handler(
                event, runtime_context("req-unsupported-content-type")
            )

        self.assert_api_error(
            response,
            400,
            "UNSUPPORTED_CONTENT_TYPE",
            "Unsupported content type",
        )

    # Verifies missing moderation records surface as the public not-found API contract.
    def test_api_handler_returns_not_found_error_contract(self) -> None:
        api_services, _api_router, api_handler = load_api_stack()
        service_module = cast(Any, api_services)
        service_module.table = FakeTable(items=[])
        event = api_runtime_event("api-moderation-result-by-image-id.json")

        with patch.object(api_handler, "capture_sample_event"):
            response = api_handler.lambda_handler(event, runtime_context("req-not-found"))

        self.assert_api_error(
            response,
            404,
            "MODERATION_RESULT_NOT_FOUND",
            "Moderation result not found",
        )

    # Verifies invalid pagination input is rejected with the expected validation error contract.
    def test_api_handler_returns_invalid_limit_error_contract(self) -> None:
        _api_services, _api_router, api_handler = load_api_stack()
        event = api_runtime_event("api-moderation-results.json")
        event["queryStringParameters"] = {"limit": "invalid"}

        with patch.object(api_handler, "capture_sample_event"):
            response = api_handler.lambda_handler(event, runtime_context("req-invalid-limit"))

        self.assert_api_error(response, 400, "INVALID_LIMIT", "Limit must be a valid integer")

    # Verifies unmatched routes are normalized into the public route-not-found error contract.
    def test_api_handler_returns_route_not_found_error_contract(self) -> None:
        _api_services, _api_router, api_handler = load_api_stack()
        event = api_runtime_event("api-moderation-results.json")
        event["rawPath"] = "/unknown-route"
        event["requestContext"]["http"]["path"] = "/unknown-route"
        event["requestContext"]["http"]["method"] = "POST"

        with patch.object(api_handler, "capture_sample_event"):
            response = api_handler.lambda_handler(event, runtime_context("req-route-not-found"))

        self.assert_api_error(response, 404, "ROUTE_NOT_FOUND", "Route not found")

    # Verifies upstream AWS client failures are translated into the generic service error contract.
    def test_api_handler_returns_aws_service_error_contract(self) -> None:
        api_services, _api_router, api_handler = load_api_stack()
        service_module = cast(Any, api_services)
        fake_s3 = FakeS3Client()
        service_module.s3 = fake_s3
        event = api_runtime_event("api-generate-upload-url.json")
        aws_error = ClientError(
            error_response={
                "Error": {"Code": "InternalError", "Message": "simulated upstream failure"}
            },
            operation_name="GeneratePresignedPost",
        )

        with patch.object(fake_s3, "generate_presigned_post", side_effect=aws_error):
            with patch.object(api_handler, "capture_sample_event"):
                response = api_handler.lambda_handler(event, runtime_context("req-aws-error"))

        self.assert_api_error(
            response,
            500,
            "AWS_SERVICE_ERROR",
            "A cloud service error occurred",
        )


if __name__ == "__main__":
    unittest.main()
