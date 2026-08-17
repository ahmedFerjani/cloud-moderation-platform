import json
from unittest.mock import patch

from _disconnect_test_setup import disconnect_handler


# Verifies disconnect handler captures events and removes existing connections
def test_handler_calls_capture_and_delete_connection() -> None:
    event = {
        "requestContext": {
            "connectionId": "conn-1",
        }
    }
    context = type("Ctx", (), {"aws_request_id": "req-1"})()

    with (
        patch.object(disconnect_handler, "capture_sample_event") as mock_capture,
        patch.object(disconnect_handler, "delete_connection") as mock_delete,
    ):
        response = disconnect_handler.lambda_handler(event, context)

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"message": "disconnected"}
    mock_capture.assert_called_once_with("websocket-disconnect", event, context)
    mock_delete.assert_called_once_with("conn-1")
