import json
from unittest.mock import MagicMock, patch

import pytest

from _api_test_setup import api_services


# Verifies limit parsing applies default and max-cap behaviors.
def test_parse_limit_default_and_cap() -> None:
    assert api_services.parse_limit({}) == 20
    assert api_services.parse_limit({"limit": "7"}) == 7
    assert api_services.parse_limit({"limit": "999"}) == 100


# Verifies invalid limits (non-numeric, zero, negative) are rejected with validation errors.
@pytest.mark.parametrize("limit", ["abc", "0", "-1"])
def test_parse_limit_invalid_raises(limit: str) -> None:
    with pytest.raises(api_services.APPError) as ctx:
        api_services.parse_limit({"limit": limit})

    assert ctx.value.code == "INVALID_LIMIT"
    assert ctx.value.status_code == 400


# Verifies upload URL generation returns stable response shape and object naming conventions.
@patch.object(api_services, "log")
def test_generate_upload_url_success(_mock_log: MagicMock) -> None:
    with patch.object(api_services.uuid, "uuid4", return_value="id-123"):
        with patch.object(api_services.s3, "generate_presigned_post") as mock_post:
            mock_post.return_value = {
                "url": "https://example.com/upload",
                "fields": {"Content-Type": "image/jpeg"},
            }
            response = api_services.generate_upload_url({"content_type": "image/jpeg"})

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["image_id"] == "id-123"
    assert body["object_key"] == "uploads/id-123.jpg"
    mock_post.assert_called_once()


# Verifies upload URL validation rejects unsupported/missing content type values.
@pytest.mark.parametrize(
    "payload,expected_code",
    [
        ({"content_type": "application/pdf"}, "UNSUPPORTED_CONTENT_TYPE"),
        ({}, "MISSING_CONTENT_TYPE"),
    ],
)
def test_generate_upload_url_validation_errors(payload: dict, expected_code: str) -> None:
    with pytest.raises(api_services.APPError) as ctx:
        api_services.generate_upload_url(payload)

    assert ctx.value.code == expected_code


# Verifies detail lookup raises not-found when DynamoDB has no matching moderation item.
def test_get_moderation_result_not_found() -> None:
    with patch.object(api_services.table, "get_item", return_value={}):
        with pytest.raises(api_services.APPError) as ctx:
            api_services.get_moderation_result("img-1")

    assert ctx.value.code == "MODERATION_RESULT_NOT_FOUND"


# Verifies detail lookup returns a successful API response for existing moderation items.
def test_get_moderation_result_success() -> None:
    item = {"image_id": "img-1", "status": "safe"}
    with patch.object(api_services.table, "get_item", return_value={"Item": item}):
        response = api_services.get_moderation_result("img-1")

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body == item


# Verifies list lookup returns items, count, and pagination key from DynamoDB scan results.
def test_get_moderation_results_success() -> None:
    with patch.object(
        api_services.table,
        "scan",
        return_value={
            "Items": [{"image_id": "img-1"}],
            "Count": 1,
            "LastEvaluatedKey": {"image_id": "img-1"},
        },
    ) as mock_scan:
        response = api_services.get_moderation_results(5)

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["count"] == 1
    assert body["items"][0]["image_id"] == "img-1"
    assert body["last_evaluated_key"] == {"image_id": "img-1"}
    mock_scan.assert_called_once_with(Limit=5)
