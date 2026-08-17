from unittest.mock import patch

from _integration_test_setup import (
    load_websocket_authorizer_stack,
    runtime_context,
    websocket_authorizer_runtime_event,
)


# Verifies missing connection tokens are denied by the websocket authorizer contract.
def test_websocket_authorizer_denies_missing_token_end_to_end() -> None:
    _services, handler = load_websocket_authorizer_stack()
    event = websocket_authorizer_runtime_event(token=None)

    with patch.object(handler, "capture_sample_event"):
        response = handler.lambda_handler(event, runtime_context("req-ws-auth-missing"))

    statement = response["policyDocument"]["Statement"][0]
    assert response["principalId"] == "anonymous"
    assert statement["Effect"] == "Deny"


# Verifies invalid tokens are denied when verification raises an exception.
def test_websocket_authorizer_denies_invalid_token_end_to_end() -> None:
    _services, handler = load_websocket_authorizer_stack()
    event = websocket_authorizer_runtime_event(token="bad-token")

    with (
        patch.object(handler, "capture_sample_event"),
        patch.object(handler, "verify_token", side_effect=Exception("invalid token")),
    ):
        response = handler.lambda_handler(event, runtime_context("req-ws-auth-invalid"))

    statement = response["policyDocument"]["Statement"][0]
    assert response["principalId"] == "anonymous"
    assert statement["Effect"] == "Deny"


# Verifies valid tokens return an allow policy and principal user context.
def test_websocket_authorizer_allows_valid_token_end_to_end() -> None:
    _services, handler = load_websocket_authorizer_stack()
    event = websocket_authorizer_runtime_event(token="good-token")

    with (
        patch.object(handler, "capture_sample_event"),
        patch.object(handler, "verify_token", return_value={"sub": "user-123"}),
    ):
        response = handler.lambda_handler(event, runtime_context("req-ws-auth-valid"))

    statement = response["policyDocument"]["Statement"][0]
    assert response["principalId"] == "user-123"
    assert statement["Effect"] == "Allow"
    assert response["context"] == {"user_id": "user-123"}
