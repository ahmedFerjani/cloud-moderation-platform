import json
from unittest.mock import patch

from _api_test_setup import api_handler


# Verifies the API handler captures sample events and delegates request routing.
def test_handler_calls_capture_and_router(api_event_factory, api_context) -> None:
    event = api_event_factory("api-moderation-results.json")

    with patch.object(api_handler, "capture_sample_event") as mock_capture:
        with patch.object(
            api_handler, "route_request", return_value={"statusCode": 200}
        ) as mock_route:
            result = api_handler.lambda_handler(event, api_context)

    assert result == {"statusCode": 200}
    mock_capture.assert_called_once_with("content-moderation-api", event, api_context)
    mock_route.assert_called_once_with(event)


# Verifies JSON decode errors from routing are translated into the public 400 contract.
def test_handler_returns_invalid_json_error_response(api_event_factory, api_context) -> None:
    event = api_event_factory("api-generate-upload-url.json")

    with patch.object(api_handler, "capture_sample_event"):
        with patch.object(
            api_handler,
            "route_request",
            side_effect=json.JSONDecodeError("bad json", "{", 0),
        ):
            result = api_handler.lambda_handler(event, api_context)

    body = json.loads(result["body"])
    assert result["statusCode"] == 400
    assert body["error"]["code"] == "INVALID_JSON"
