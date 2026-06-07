from decimal import Decimal
from unittest.mock import patch

import services.image_labeling_service as image_labeling_service


# Verifies Rekognition confidence values are normalized to Decimal for DynamoDB compatibility.
def test_detect_moderation_labels_maps_confidence_to_decimal() -> None:
    with patch.object(
        image_labeling_service.rekognition, "detect_moderation_labels"
    ) as mock_detect:
        mock_detect.return_value = {
            "ModerationLabels": [
                {
                    "Name": "Violence",
                    "Confidence": 98.7,
                    "ParentName": "Graphic Violence",
                }
            ]
        }

        labels = image_labeling_service.detect_moderation_labels("bucket", "uploads/a.jpg")

    assert labels[0]["Name"] == "Violence"
    assert labels[0]["Confidence"] == Decimal("98.7")
    assert labels[0]["ParentName"] == "Graphic Violence"
    mock_detect.assert_called_once_with(
        Image={"S3Object": {"Bucket": "bucket", "Name": "uploads/a.jpg"}},
        MinConfidence=image_labeling_service.MIN_CONFIDENCE,
    )


# Verifies Textract line blocks are aggregated into a newline-separated string.
def test_extract_text_from_image_returns_joined_lines() -> None:
    with patch.object(image_labeling_service.textract, "detect_document_text") as mock_detect:
        mock_detect.return_value = {
            "Blocks": [
                {"BlockType": "LINE", "Text": "First line"},
                {"BlockType": "WORD", "Text": "ignored"},
                {"BlockType": "LINE", "Text": "Second line"},
            ]
        }

        extracted = image_labeling_service.extract_text_from_image("bucket", "uploads/a.jpg")

    assert extracted == "First line\nSecond line"
    mock_detect.assert_called_once_with(
        Document={"S3Object": {"Bucket": "bucket", "Name": "uploads/a.jpg"}}
    )


# Verifies Textract extraction returns None when no non-empty line blocks are present.
def test_extract_text_from_image_returns_none_without_lines() -> None:
    with patch.object(image_labeling_service.textract, "detect_document_text") as mock_detect:
        mock_detect.return_value = {
            "Blocks": [
                {"BlockType": "WORD", "Text": "token"},
                {"BlockType": "LINE", "Text": "   "},
            ]
        }

        extracted = image_labeling_service.extract_text_from_image("bucket", "uploads/a.jpg")

    assert extracted is None
