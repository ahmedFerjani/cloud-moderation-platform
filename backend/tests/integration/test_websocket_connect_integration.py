import json
from typing import Any, cast
from unittest.mock import patch

from _integration_test_setup import (
    FakeTable,
    load_websocket_connect_stack,
    runtime_context,
    websocket_connect_runtime_event,
)


def assert_api_error(response: dict, status_code: int, code: str, message: str) -> None:
    body = json.loads(response["body"])
    assert response["statusCode"] == status_code
    assert response["headers"]["Content-Type"] == "application/json"
    assert response["headers"]["Access-Control-Allow-Origin"] == "*"
    assert body["error"]["code"] == code
    assert body["error"]["message"] == message


# Verifies websocket connect persists connection metadata and returns success payload.
def test_websocket_connect_persists_connection_end_to_end() -> None:
    services, handler = load_websocket_connect_stack()
    service_module = cast(Any, services)
    fake_table = FakeTable()
    service_module.table = fake_table

    event = websocket_connect_runtime_event("conn-1", "user-1")

    with (
        patch.object(handler, "capture_sample_event"),
        patch.object(service_module.time, "time", return_value=1_000),
    ):
        response = handler.lambda_handler(event, runtime_context("req-ws-connect"))

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"message": "connected"}
    assert len(fake_table.put_items) == 1
    item = fake_table.put_items[0]
    assert item["connectionId"] == "conn-1"
    assert item["userId"] == "user-1"
    assert item["expiresAt"] == 1_000 + service_module.CONNECTION_TTL_SECONDS


# Verifies malformed connect events return the standard internal server error contract.
def test_websocket_connect_returns_internal_error_when_authorizer_missing() -> None:
    _services, handler = load_websocket_connect_stack()
    event = {"requestContext": {"connectionId": "conn-1", "routeKey": "$connect"}}

    with patch.object(handler, "capture_sample_event"):
        response = handler.lambda_handler(event, runtime_context("req-ws-connect-missing-auth"))

    assert_api_error(
        response,
        500,
        "INTERNAL_SERVER_ERROR",
        "An unexpected server error occurred",
    )
