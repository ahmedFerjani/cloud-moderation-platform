import pytest

from _api_test_setup import api_validation


# Verifies limit parsing applies default and max-cap behaviors.
def test_parse_limit_default_and_cap() -> None:
    assert api_validation.parse_limit({}) == 20
    assert api_validation.parse_limit({"limit": "7"}) == 7
    assert api_validation.parse_limit({"limit": "999"}) == 100


# Verifies invalid limits (non-numeric, zero, negative) are rejected with validation errors.
@pytest.mark.parametrize("limit", ["abc", "0", "-1"])
def test_parse_limit_invalid_raises(limit: str) -> None:
    with pytest.raises(api_validation.APPError) as ctx:
        api_validation.parse_limit({"limit": limit})

    assert ctx.value.code == "INVALID_LIMIT"
    assert ctx.value.status_code == 400


# Verifies pagination cursor parsing accepts missing and valid JSON object values.
def test_parse_last_evaluated_key_valid() -> None:
    assert api_validation.parse_last_evaluated_key({}) is None
    assert api_validation.parse_last_evaluated_key({"last_evaluated_key": ""}) is None
    assert api_validation.parse_last_evaluated_key(
        {"last_evaluated_key": '{"image_id": "img-1"}'}
    ) == {"image_id": "img-1"}


# Verifies invalid pagination cursor shapes and payloads are rejected.
@pytest.mark.parametrize(
    "cursor",
    ["not-json", "[]", '{"image_id": 1}', '{"image_id": "img-1", "page": 2}'],
)
def test_parse_last_evaluated_key_invalid_raises(cursor: str) -> None:
    with pytest.raises(api_validation.APPError) as ctx:
        api_validation.parse_last_evaluated_key({"last_evaluated_key": cursor})

    assert ctx.value.code == "INVALID_LAST_EVALUATED_KEY"
    assert ctx.value.status_code == 400


# Verifies content_type normalization accepts both single and list values.
@pytest.mark.parametrize(
    "payload,expected",
    [
        ({"content_type": "image/jpeg"}, ["image/jpeg"]),
        ({"content_type": ["image/jpeg", "image/png"]}, ["image/jpeg", "image/png"]),
    ],
)
def test_normalize_content_types_success(payload: dict, expected: list[str]) -> None:
    assert api_validation.normalize_content_types(payload) == expected


# Verifies content_type normalization enforces type, allowed values, and file-count limits.
@pytest.mark.parametrize(
    "payload,expected_code,expected_status_code",
    [
        ({"content_type": "application/pdf"}, "UNSUPPORTED_CONTENT_TYPE", 415),
        ({"content_type": ""}, "UNSUPPORTED_CONTENT_TYPE", 415),
        ({}, "MISSING_CONTENT_TYPE", 400),
        ({"content_type": []}, "MISSING_CONTENT_TYPE", 400),
        ({"content_type": 123}, "INVALID_CONTENT_TYPE", 400),
        ({"content_type": ["image/jpeg", 123]}, "INVALID_CONTENT_TYPE", 400),
        ({"content_type": ["application/pdf"]}, "UNSUPPORTED_CONTENT_TYPE", 415),
        ({"content_type": ["image/jpeg"] * 11}, "TOO_MANY_FILES", 422),
    ],
)
def test_normalize_content_types_validation_errors(
    payload: dict, expected_code: str, expected_status_code: int
) -> None:
    with pytest.raises(api_validation.APPError) as ctx:
        api_validation.normalize_content_types(payload)

    assert ctx.value.code == expected_code
    assert ctx.value.status_code == expected_status_code
