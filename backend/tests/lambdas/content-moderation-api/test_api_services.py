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


# Verifies pagination cursor parsing accepts missing and valid JSON object values.
def test_parse_last_evaluated_key_valid() -> None:
    assert api_services.parse_last_evaluated_key({}) is None
    assert api_services.parse_last_evaluated_key({"last_evaluated_key": ""}) is None
    assert api_services.parse_last_evaluated_key(
        {"last_evaluated_key": '{"image_id": "img-1"}'}
    ) == {"image_id": "img-1"}


# Verifies invalid pagination cursor shapes and payloads are rejected.
@pytest.mark.parametrize(
    "cursor",
    ["not-json", "[]", '{"image_id": 1}', '{"image_id": "img-1", "page": 2}'],
)
def test_parse_last_evaluated_key_invalid_raises(cursor: str) -> None:
    with pytest.raises(api_services.APPError) as ctx:
        api_services.parse_last_evaluated_key({"last_evaluated_key": cursor})

    assert ctx.value.code == "INVALID_LAST_EVALUATED_KEY"
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
    assert body["count"] == 1
    assert body["uploads"][0]["image_id"] == "id-123"
    assert body["uploads"][0]["object_key"] == "uploads/id-123.jpg"
    assert body["expires_in"] == api_services.UPLOAD_URL_EXPIRES_IN_SECONDS
    assert body["max_upload_size_bytes"] == api_services.MAX_UPLOAD_FILE_SIZE_BYTES
    mock_post.assert_called_once()


# Verifies batch upload URL generation returns one presigned upload payload per requested content type.
@patch.object(api_services, "log")
def test_generate_upload_url_batch_success(_mock_log: MagicMock) -> None:
    with patch.object(
        api_services.uuid,
        "uuid4",
        side_effect=["id-1", "id-2"],
    ):
        with patch.object(api_services.s3, "generate_presigned_post") as mock_post:
            mock_post.return_value = {
                "url": "https://example.com/upload",
                "fields": {"Content-Type": "image/jpeg"},
            }
            response = api_services.generate_upload_url(
                {"content_type": ["image/jpeg", "image/png"]}
            )

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["count"] == 2
    assert len(body["uploads"]) == 2
    assert body["uploads"][0]["image_id"] == "id-1"
    assert body["uploads"][1]["image_id"] == "id-2"
    assert mock_post.call_count == 2


# Verifies exactly MAX_UPLOAD_FILES content types are accepted in a single batch request.
@patch.object(api_services, "log")
def test_generate_upload_url_accepts_max_files(_mock_log: MagicMock) -> None:
    max_files = api_services.MAX_UPLOAD_FILES
    content_types = ["image/jpeg"] * max_files

    with patch.object(
        api_services.uuid,
        "uuid4",
        side_effect=[f"id-{index}" for index in range(max_files)],
    ):
        with patch.object(api_services.s3, "generate_presigned_post") as mock_post:
            mock_post.return_value = {
                "url": "https://example.com/upload",
                "fields": {"Content-Type": "image/jpeg"},
            }
            response = api_services.generate_upload_url({"content_type": content_types})

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["count"] == max_files
    assert len(body["uploads"]) == max_files
    assert mock_post.call_count == max_files


# Verifies upload URL validation rejects unsupported/missing content type values.
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
def test_generate_upload_url_validation_errors(
    payload: dict, expected_code: str, expected_status_code: int
) -> None:
    with pytest.raises(api_services.APPError) as ctx:
        api_services.generate_upload_url(payload)

    assert ctx.value.code == expected_code
    assert ctx.value.status_code == expected_status_code


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


# Verifies list lookup forwards optional last_evaluated_key cursor to DynamoDB scan.
def test_get_moderation_results_success_with_last_evaluated_key() -> None:
    with patch.object(
        api_services.table,
        "scan",
        return_value={
            "Items": [{"image_id": "img-2"}],
            "Count": 1,
            "LastEvaluatedKey": None,
        },
    ) as mock_scan:
        response = api_services.get_moderation_results(5, {"image_id": "img-1"})

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["count"] == 1
    assert body["items"][0]["image_id"] == "img-2"
    assert body["last_evaluated_key"] is None
    mock_scan.assert_called_once_with(Limit=5, ExclusiveStartKey={"image_id": "img-1"})
