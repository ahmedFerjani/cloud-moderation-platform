from unittest.mock import patch

from _authorizer_test_setup import authorizer_handler


# Verifies missing token requests are denied without calling token verification
def test_handler_denies_when_token_missing() -> None:
    event = {"methodArn": "arn:aws:execute-api:region:acct:api/stage/GET/$connect"}
    context = type("Ctx", (), {"aws_request_id": "req-1"})()

    with (
        patch.object(authorizer_handler, "capture_sample_event") as mock_capture,
        patch.object(authorizer_handler, "verify_token") as mock_verify,
    ):
        response = authorizer_handler.lambda_handler(event, context)

    statement = response["policyDocument"]["Statement"][0]
    assert response["principalId"] == "anonymous"
    assert statement["Effect"] == "Deny"
    mock_capture.assert_called_once_with("websocket-authorizer", event, context)
    mock_verify.assert_not_called()


# Verifies invalid tokens are denied after verification fails
def test_handler_denies_when_token_verification_fails() -> None:
    event = {
        "methodArn": "arn:aws:execute-api:region:acct:api/stage/GET/$connect",
        "queryStringParameters": {"token": "bad-token"},
    }
    context = type("Ctx", (), {"aws_request_id": "req-2"})()

    with (
        patch.object(authorizer_handler, "capture_sample_event"),
        patch.object(authorizer_handler, "verify_token", side_effect=Exception("invalid")),
    ):
        response = authorizer_handler.lambda_handler(event, context)

    statement = response["policyDocument"]["Statement"][0]
    assert response["principalId"] == "anonymous"
    assert statement["Effect"] == "Deny"


# Verifies valid tokens return an allow policy and user context
def test_handler_allows_when_token_is_valid() -> None:
    event = {
        "methodArn": "arn:aws:execute-api:region:acct:api/stage/GET/$connect",
        "queryStringParameters": {"token": "good-token"},
    }
    context = type("Ctx", (), {"aws_request_id": "req-3"})()

    with (
        patch.object(authorizer_handler, "capture_sample_event"),
        patch.object(authorizer_handler, "verify_token", return_value={"sub": "user-123"}),
    ):
        response = authorizer_handler.lambda_handler(event, context)

    statement = response["policyDocument"]["Statement"][0]
    assert response["principalId"] == "user-123"
    assert statement["Effect"] == "Allow"
    assert response["context"] == {"user_id": "user-123"}
