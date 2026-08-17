import json
from unittest.mock import patch

from _connect_test_setup import connect_handler


# Verifies connect handler captures events and persists a new connection.
def test_handler_calls_capture_and_save_connection() -> None:
    event = {
        "requestContext": {
            "connectionId": "conn-1",
            "authorizer": {"user_id": "user-1"},
        }
    }
    context = type("Ctx", (), {"aws_request_id": "req-1"})()

    with (
        patch.object(connect_handler, "capture_sample_event") as mock_capture,
        patch.object(connect_handler, "save_connection") as mock_save,
    ):
        response = connect_handler.lambda_handler(event, context)

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"message": "connected"}
    mock_capture.assert_called_once_with("websocket-connect", event, context)
    mock_save.assert_called_once_with("conn-1", "user-1")
