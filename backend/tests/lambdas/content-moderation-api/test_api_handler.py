import json
import unittest
from unittest.mock import patch

from _api_test_setup import api_handler, api_runtime_event


class ApiHandlerTests(unittest.TestCase):
    # Verifies the API handler captures sample events and delegates request routing.
    def test_handler_calls_capture_and_router(self) -> None:
        event = api_runtime_event("api-moderation-results.json")
        context = type("Ctx", (), {"aws_request_id": "req-1"})()

        with patch.object(api_handler, "capture_sample_event") as mock_capture:
            with patch.object(
                api_handler, "route_request", return_value={"statusCode": 200}
            ) as mock_route:
                result = api_handler.lambda_handler(event, context)

        self.assertEqual(result, {"statusCode": 200})
        mock_capture.assert_called_once_with("content-moderation-api", event, context)
        mock_route.assert_called_once_with(event)

    # Verifies JSON decode errors from routing are translated into the public 400 contract.
    def test_handler_returns_invalid_json_error_response(self) -> None:
        event = api_runtime_event("api-generate-upload-url.json")
        context = type("Ctx", (), {"aws_request_id": "req-1"})()

        with patch.object(api_handler, "capture_sample_event"):
            with patch.object(
                api_handler,
                "route_request",
                side_effect=json.JSONDecodeError("bad json", "{", 0),
            ):
                result = api_handler.lambda_handler(event, context)

        body = json.loads(result["body"])
        self.assertEqual(result["statusCode"], 400)
        self.assertEqual(body["error"]["code"], "INVALID_JSON")


if __name__ == "__main__":
    unittest.main()
