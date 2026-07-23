import json
from unittest.mock import MagicMock, patch

import pytest

from _api_test_setup import api_services, api_validation


# Verifies upload URL generation returns stable response shape and object naming conventions.
@patch.object(api_services, "log")
def test_generate_upload_url_success(_mock_log: MagicMock) -> None:
    user_id = "user-123"
    with (
        patch.object(api_services.uuid, "uuid4", return_value="id-123"),
        patch.object(api_services.s3, "generate_presigned_post") as mock_post,
    ):
        mock_post.return_value = {
            "url": "https://example.com/upload",
            "fields": {"Content-Type": "image/jpeg"},
        }
        response = api_services.generate_upload_url({"content_type": "image/jpeg"}, user_id)

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["count"] == 1
    assert body["uploads"][0]["image_id"] == "id-123"
    assert body["uploads"][0]["object_key"] == "uploads/user-123/id-123.jpg"
    assert body["expires_in"] == api_services.UPLOAD_URL_EXPIRES_IN_SECONDS
    assert body["max_upload_size_bytes"] == api_services.MAX_UPLOAD_FILE_SIZE_BYTES
    mock_post.assert_called_once()


# Verifies one presigned upload URL generation per content type.
@patch.object(api_services, "log")
def test_generate_upload_url_batch_success(_mock_log: MagicMock) -> None:
    user_id = "user-123"
    with (
        patch.object(api_services.uuid, "uuid4", side_effect=["id-1", "id-2"]),
        patch.object(api_services.s3, "generate_presigned_post") as mock_post,
    ):
        mock_post.return_value = {
            "url": "https://example.com/upload",
            "fields": {"Content-Type": "image/jpeg"},
        }
        response = api_services.generate_upload_url(
            {"content_type": ["image/jpeg", "image/png"]}, user_id
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
    max_files = api_validation.MAX_UPLOAD_FILES
    user_id = "user-123"
    content_types = ["image/jpeg"] * max_files

    with (
        patch.object(
            api_services.uuid,
            "uuid4",
            side_effect=[f"id-{index}" for index in range(max_files)],
        ),
        patch.object(api_services.s3, "generate_presigned_post") as mock_post,
    ):
        mock_post.return_value = {
            "url": "https://example.com/upload",
            "fields": {"Content-Type": "image/jpeg"},
        }
        response = api_services.generate_upload_url({"content_type": content_types}, user_id)

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["count"] == max_files
    assert len(body["uploads"]) == max_files
    assert mock_post.call_count == max_files


# Verifies detail lookup raises not-found when DynamoDB has no matching moderation item.
def test_get_moderation_result_not_found() -> None:
    with (
        patch.object(api_services.table, "get_item", return_value={}),
        pytest.raises(api_services.APPError) as ctx,
    ):
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
