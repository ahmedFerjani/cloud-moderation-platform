import hashlib
import json
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from _orchestrator_test_setup import orchestrator_services


# Verifies image IDs are derived from S3 object keys consistently.
def test_extract_image_id_from_s3_key() -> None:
    result = orchestrator_services.extract_image_id_from_s3_key("uploads/sample-image.jpg")

    assert result == "sample-image"


# Verifies upload size validation rejects empty/oversized files and accepts valid boundaries.
def test_validate_upload_size_boundaries() -> None:
    with pytest.raises(orchestrator_services.APPError):
        orchestrator_services.validate_upload_size(0)

    with pytest.raises(orchestrator_services.APPError):
        orchestrator_services.validate_upload_size(6 * 1024 * 1024)

    orchestrator_services.validate_upload_size(1)


# Verifies stored moderation status toggles between safe and unsafe based on labels.
def test_store_moderation_result_status_safe_or_unsafe() -> None:
    with patch.object(orchestrator_services.table, "put_item") as mock_put:
        orchestrator_services.store_moderation_result([], "uploads/a.jpg", "hash-1")
        first_item = mock_put.call_args.kwargs["Item"]

        orchestrator_services.store_moderation_result(
            [{"Name": "Violence", "Confidence": 99}],
            "uploads/b.jpg",
            "hash-2",
        )
        second_item = mock_put.call_args.kwargs["Item"]

        orchestrator_services.store_moderation_result(
            [],
            "uploads/c.jpg",
            "hash-3",
            extracted_text="Detected text",
        )
        third_item = mock_put.call_args.kwargs["Item"]

    assert first_item["status"] == "safe"
    assert not first_item["unsafe_detected"]
    assert second_item["status"] == "unsafe"
    assert second_item["unsafe_detected"]
    assert "extracted_text" not in first_item
    assert "extracted_text" in third_item
    assert third_item["extracted_text"] == "Detected text"


# Verifies Rekognition confidence values are normalized to Decimal for DynamoDB compatibility.
def test_detect_moderation_labels_maps_confidence_to_decimal() -> None:
    with patch.object(orchestrator_services.rekognition, "detect_moderation_labels") as mock_detect:
        mock_detect.return_value = {
            "ModerationLabels": [
                {
                    "Name": "Violence",
                    "Confidence": 98.7,
                    "ParentName": "Graphic Violence",
                }
            ]
        }

        labels = orchestrator_services.detect_moderation_labels("bucket", "uploads/a.jpg")

    assert labels[0]["Name"] == "Violence"
    assert labels[0]["Confidence"] == Decimal("98.7")
    assert labels[0]["ParentName"] == "Graphic Violence"
    mock_detect.assert_called_once_with(
        Image={"S3Object": {"Bucket": "bucket", "Name": "uploads/a.jpg"}},
        MinConfidence=orchestrator_services.MIN_CONFIDENCE,
    )


# Verifies Textract line blocks are aggregated into a newline-separated string.
def test_extract_text_from_image_returns_joined_lines() -> None:
    with patch.object(orchestrator_services.textract, "detect_document_text") as mock_detect:
        mock_detect.return_value = {
            "Blocks": [
                {"BlockType": "LINE", "Text": "First line"},
                {"BlockType": "WORD", "Text": "ignored"},
                {"BlockType": "LINE", "Text": "Second line"},
            ]
        }

        extracted = orchestrator_services.extract_text_from_image("bucket", "uploads/a.jpg")

    assert extracted == "First line\nSecond line"
    mock_detect.assert_called_once_with(
        Document={"S3Object": {"Bucket": "bucket", "Name": "uploads/a.jpg"}}
    )


# Verifies Textract extraction returns None when no non-empty line blocks are present.
def test_extract_text_from_image_returns_none_without_lines() -> None:
    with patch.object(orchestrator_services.textract, "detect_document_text") as mock_detect:
        mock_detect.return_value = {
            "Blocks": [
                {"BlockType": "WORD", "Text": "token"},
                {"BlockType": "LINE", "Text": "   "},
            ]
        }

        extracted = orchestrator_services.extract_text_from_image("bucket", "uploads/a.jpg")

    assert extracted is None


# Verifies success notifications are skipped when topic configuration is absent.
def test_send_success_notification_skips_without_topic() -> None:
    with patch.object(orchestrator_services, "SNS_SUCCESS_TOPIC_ARN", None):
        with patch.object(orchestrator_services.sns, "publish") as mock_publish:
            orchestrator_services.send_success_notification("uploads/a.jpg", [])

    mock_publish.assert_not_called()


# Verifies success notifications include the expected envelope and moderation summary payload.
def test_send_success_notification_publishes_payload() -> None:
    with patch.object(
        orchestrator_services,
        "SNS_SUCCESS_TOPIC_ARN",
        "arn:aws:sns:us-east-1:123456789012:topic",
    ):
        with patch.object(orchestrator_services.sns, "publish") as mock_publish:
            orchestrator_services.send_success_notification("uploads/a.jpg", [{"Name": "Violence"}])

    mock_publish.assert_called_once()
    publish_kwargs = mock_publish.call_args.kwargs
    assert publish_kwargs["TopicArn"] == "arn:aws:sns:us-east-1:123456789012:topic"
    assert publish_kwargs["Subject"] == "Image Moderation Completed"
    payload = json.loads(publish_kwargs["Message"])
    assert payload["event_type"] == "SUCCESS"
    assert payload["image_id"] == "a"
    assert payload["s3_key"] == "uploads/a.jpg"
    assert payload["status"] == "unsafe"
    assert payload["unsafe_detected"]
    assert payload["labels_count"] == 1


# Verifies image download reads bytes from the S3 object body stream.
def test_download_image_reads_s3_body() -> None:
    body = SimpleNamespace(read=lambda: b"img-bytes")
    with patch.object(
        orchestrator_services.s3, "get_object", return_value={"Body": body}
    ) as mock_get:
        result = orchestrator_services.download_image("bucket", "uploads/a.jpg")

    assert result == b"img-bytes"
    mock_get.assert_called_once_with(Bucket="bucket", Key="uploads/a.jpg")


# Verifies invalid uploads are deleted from S3 with the expected bucket and key.
def test_delete_invalid_upload_calls_s3_delete() -> None:
    with patch.object(orchestrator_services.s3, "delete_object") as mock_delete:
        orchestrator_services.delete_invalid_upload("bucket", "uploads/a.jpg")

    mock_delete.assert_called_once_with(Bucket="bucket", Key="uploads/a.jpg")


# Verifies non-image payloads raise the invalid-image business error.
def test_validate_image_invalid_file_raises() -> None:
    with patch.object(orchestrator_services.Image, "open", side_effect=Exception):
        with pytest.raises(orchestrator_services.APPError) as ctx:
            orchestrator_services.validate_image(b"not-an-image")

    assert ctx.value.code == "INVALID_IMAGE_FILE"


# Verifies unsupported formats raise the unsupported-image-type business error.
def test_validate_image_unsupported_type_raises() -> None:
    fake_image = SimpleNamespace(format="GIF")
    with patch.object(orchestrator_services.Image, "open", return_value=fake_image):
        with pytest.raises(orchestrator_services.APPError) as ctx:
            orchestrator_services.validate_image(b"gif-bytes")

    assert ctx.value.code == "UNSUPPORTED_IMAGE_TYPE"


# Verifies supported image formats are normalized to lowercase canonical values.
def test_validate_image_supported_type_returns_lowercase() -> None:
    fake_image = SimpleNamespace(format="JPEG")
    with patch.object(orchestrator_services.Image, "open", return_value=fake_image):
        result = orchestrator_services.validate_image(b"jpeg-bytes")

    assert result == "jpeg"


# Verifies hash generation is deterministic for a given byte payload.
def test_generate_image_hash_is_deterministic() -> None:
    data = b"abc"
    expected = hashlib.sha256(data).hexdigest()

    assert orchestrator_services.generate_image_hash(data) == expected


# Verifies duplicate lookup returns None when no hash match exists.
def test_find_existing_image_returns_none_when_missing() -> None:
    with patch.object(
        orchestrator_services.table, "query", return_value={"Items": []}
    ) as mock_query:
        result = orchestrator_services.find_existing_image("hash-1")

    assert result is None
    assert mock_query.call_args.kwargs["IndexName"] == "image_hash"
    assert mock_query.call_args.kwargs["Limit"] == 1


# Verifies duplicate lookup returns only the first match from the image-hash index query.
def test_find_existing_image_returns_first_item() -> None:
    expected = {"image_id": "img-1", "status": "safe"}
    with patch.object(
        orchestrator_services.table,
        "query",
        return_value={"Items": [expected, {"image_id": "img-2"}]},
    ):
        result = orchestrator_services.find_existing_image("hash-1")

    assert result == expected
