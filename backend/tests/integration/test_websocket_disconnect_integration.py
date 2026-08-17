import json
from typing import Any, cast
from unittest.mock import patch

from _integration_test_setup import (
    FakeTable,
    load_websocket_disconnect_stack,
    runtime_context,
    websocket_disconnect_runtime_event,
)


# Verifies websocket disconnect removes the stored connection and returns success payload.
def test_websocket_disconnect_removes_connection_end_to_end() -> None:
    services, handler = load_websocket_disconnect_stack()
    service_module = cast(Any, services)
    fake_table = FakeTable()
    service_module.table = fake_table

    event = websocket_disconnect_runtime_event("conn-1")

    with patch.object(handler, "capture_sample_event"):
        response = handler.lambda_handler(event, runtime_context("req-ws-disconnect"))

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"message": "disconnected"}
    assert fake_table.deleted_keys == [{"connectionId": "conn-1"}]
