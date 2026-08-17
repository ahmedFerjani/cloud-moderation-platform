import pytest

from _authorizer_test_setup import authorizer_services
from common.exceptions import APPError


# Verifies only Cognito access tokens are accepted
def test_verify_token_rejects_non_access_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        authorizer_services,
        "_decode_verified_claims",
        lambda _token: {"token_use": "id", "client_id": authorizer_services.APP_CLIENT_ID},
    )

    with pytest.raises(APPError) as exc_info:
        authorizer_services.verify_token("token")

    assert exc_info.value.code == "INVALID_TOKEN_USE"


# Verifies tokens with unexpected client_id are rejected
def test_verify_token_rejects_wrong_client_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        authorizer_services,
        "_decode_verified_claims",
        lambda _token: {"token_use": "access", "client_id": "wrong-client"},
    )

    with pytest.raises(APPError) as exc_info:
        authorizer_services.verify_token("token")

    assert exc_info.value.code == "INVALID_CLIENT_ID"


# Verifies verified access token claims are returned unchanged
def test_verify_token_returns_claims_for_valid_access_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    claims = {
        "sub": "user-123",
        "token_use": "access",
        "client_id": authorizer_services.APP_CLIENT_ID,
    }

    monkeypatch.setattr(authorizer_services, "_decode_verified_claims", lambda _token: claims)
    result = authorizer_services.verify_token("token")

    assert result == claims
