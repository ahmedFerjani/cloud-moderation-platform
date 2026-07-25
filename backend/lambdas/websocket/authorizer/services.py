import http.client
import json
import os
from urllib.parse import ParseResult, urlparse
from common.exceptions import APPError
from jose import jwt
from jose.exceptions import JWTError

USER_POOL_ID = os.environ["USER_POOL_ID"]
REGION = os.environ["AWS_REGION"]
APP_CLIENT_ID = os.environ["APP_CLIENT_ID"]

ISSUER = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}"
JWKS_URL = f"{ISSUER}/.well-known/jwks.json"

_jwks_cache: list[dict] | None = None


def _invalidate_jwks_cache() -> None:
    global _jwks_cache
    _jwks_cache = None


def _validate_jwks_url(parsed: ParseResult) -> str:
    if parsed.scheme != "https":
        raise APPError("INVALID_JWKS_URL", "JWKS URL must use HTTPS", 500)
    hostname = parsed.hostname
    if hostname is None:
        raise APPError("INVALID_JWKS_URL", "JWKS URL host is missing", 500)
    expected_host = f"cognito-idp.{REGION}.amazonaws.com"
    if hostname != expected_host:
        raise APPError("INVALID_JWKS_URL", "JWKS URL host is invalid", 500)
    if parsed.username or parsed.password:
        raise APPError("INVALID_JWKS_URL", "JWKS URL must not include user info", 500)
    if parsed.params or parsed.query or parsed.fragment:
        raise APPError(
            "INVALID_JWKS_URL",
            "JWKS URL must not include params, query, or fragment",
            500,
        )

    return hostname


def _get_jwks() -> list[dict]:
    global _jwks_cache

    if _jwks_cache is None:
        parsed = urlparse(JWKS_URL)
        hostname = _validate_jwks_url(parsed)

        connection = http.client.HTTPSConnection(hostname, parsed.port or 443, timeout=5)

        try:
            connection.request("GET", parsed.path)
            response = connection.getresponse()

            if response.status != 200:
                raise APPError(
                    "JWKS_FETCH_FAILED",
                    f"Failed to fetch JWKS: HTTP {response.status}",
                    500,
                )

            content_type = response.getheader("Content-Type", "")
            if "application/json" not in content_type:
                raise APPError(
                    "INVALID_JWKS_RESPONSE",
                    "JWKS endpoint returned an unexpected content type",
                    500,
                )

            try:
                payload = json.loads(response.read())
            except json.JSONDecodeError as exc:
                raise APPError(
                    "INVALID_JWKS_RESPONSE",
                    "JWKS response is not valid JSON",
                    500,
                ) from exc

            keys = payload.get("keys")

            if not isinstance(keys, list):
                raise APPError(
                    "INVALID_JWKS_RESPONSE",
                    "JWKS response is missing signing keys",
                    500,
                )

            _jwks_cache = keys
        finally:
            connection.close()

    return _jwks_cache


def _decode_verified_claims(token: str) -> dict:
    last_error = None

    # Try once with cache, then refresh JWKS one time in case keys rotated.
    for attempt in range(2):
        for key_data in _get_jwks():
            try:
                return jwt.decode(
                    token,
                    key_data,
                    algorithms=["RS256"],
                    issuer=ISSUER,
                    options={"verify_aud": False},  # Cognito access tokens use client_id, not aud
                )
            except JWTError as exc:
                last_error = exc

        if attempt == 0:
            _invalidate_jwks_cache()

    if last_error is not None:
        raise APPError(
            "TOKEN_SIGNATURE_INVALID",
            "Token signature verification failed",
            401,
        ) from last_error

    raise APPError("JWKS_KEYS_MISSING", "No signing keys available in JWKS", 401)


def verify_token(token: str) -> dict:
    claims = _decode_verified_claims(token)

    token_use = claims.get("token_use")
    if token_use != "access":
        raise APPError("INVALID_TOKEN_USE", "Not an access token", 401)

    client_id = claims.get("client_id")
    if client_id != APP_CLIENT_ID:
        raise APPError("INVALID_CLIENT_ID", "Invalid client_id", 401)

    return claims
