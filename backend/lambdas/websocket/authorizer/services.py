import json
import os
import urllib.request
from jose import jwt

USER_POOL_ID = os.environ["USER_POOL_ID"]
REGION = os.environ["AWS_REGION"]
APP_CLIENT_ID = os.environ["APP_CLIENT_ID"]

ISSUER = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}"
JWKS_URL = f"{ISSUER}/.well-known/jwks.json"

_jwks_cache = None


def _get_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        with urllib.request.urlopen(JWKS_URL) as response:
            _jwks_cache = json.loads(response.read())["keys"]
    return _jwks_cache


def _find_signing_key(kid):
    for key in _get_jwks():
        if key["kid"] == kid:
            return key
    return None


def verify_token(token):
    headers = jwt.get_unverified_headers(token)

    if headers.get("alg") != "RS256":
        raise ValueError(f"Unsupported algorithm: {headers.get('alg')}")

    key_data = _find_signing_key(headers["kid"])
    if key_data is None:
        raise ValueError("Signing key not found in JWKS")

    claims = jwt.decode(
        token,
        key_data,
        algorithms=["RS256"],
        issuer=ISSUER,
        options={"verify_aud": False},  # Cognito access tokens use client_id, not aud
    )

    if claims["token_use"] != "access":
        raise ValueError("Not an access token")
    if claims["client_id"] != APP_CLIENT_ID:
        raise ValueError("Invalid client_id")

    return claims
