import hashlib
import json
import unittest
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from _orchestrator_test_setup import orchestrator_services


class OrchestratorServicesTests(unittest.TestCase):
    def test_extract_image_id_from_s3_key(self) -> None:
        result = orchestrator_services.extract_image_id_from_s3_key(
            "uploads/sample-image.jpg"
        )

        self.assertEqual(result, "sample-image")

    def test_validate_upload_size_boundaries(self) -> None:
        with self.assertRaises(orchestrator_services.APPError):
            orchestrator_services.validate_upload_size(0)

        with self.assertRaises(orchestrator_services.APPError):
            orchestrator_services.validate_upload_size(6 * 1024 * 1024)

        orchestrator_services.validate_upload_size(1)

    def test_store_moderation_result_status_safe_or_unsafe(self) -> None:
        with patch.object(orchestrator_services.table, "put_item") as mock_put:
            orchestrator_services.store_moderation_result([], "uploads/a.jpg", "hash-1")
            first_item = mock_put.call_args.kwargs["Item"]

            orchestrator_services.store_moderation_result(
                [{"Name": "Violence", "Confidence": 99}],
                "uploads/b.jpg",
                "hash-2",
            )
            second_item = mock_put.call_args.kwargs["Item"]

        self.assertEqual(first_item["status"], "safe")
        self.assertFalse(first_item["unsafe_detected"])
        self.assertEqual(second_item["status"], "unsafe")
        self.assertTrue(second_item["unsafe_detected"])

    def test_detect_moderation_labels_maps_confidence_to_decimal(self) -> None:
        with patch.object(
            orchestrator_services.rekognition, "detect_moderation_labels"
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

            labels = orchestrator_services.detect_moderation_labels(
                "bucket", "uploads/a.jpg"
            )

        self.assertEqual(labels[0]["Name"], "Violence")
        self.assertEqual(labels[0]["Confidence"], Decimal("98.7"))
        self.assertEqual(labels[0]["ParentName"], "Graphic Violence")
        mock_detect.assert_called_once_with(
            Image={"S3Object": {"Bucket": "bucket", "Name": "uploads/a.jpg"}},
            MinConfidence=orchestrator_services.MIN_CONFIDENCE,
        )

    def test_send_success_notification_skips_without_topic(self) -> None:
        with patch.object(orchestrator_services, "SNS_SUCCESS_TOPIC_ARN", None):
            with patch.object(orchestrator_services.sns, "publish") as mock_publish:
                orchestrator_services.send_success_notification("uploads/a.jpg", [])

        mock_publish.assert_not_called()

    def test_send_success_notification_publishes_payload(self) -> None:
        with patch.object(
            orchestrator_services,
            "SNS_SUCCESS_TOPIC_ARN",
            "arn:aws:sns:us-east-1:123456789012:topic",
        ):
            with patch.object(orchestrator_services.sns, "publish") as mock_publish:
                orchestrator_services.send_success_notification(
                    "uploads/a.jpg", [{"Name": "Violence"}]
                )

        mock_publish.assert_called_once()
        publish_kwargs = mock_publish.call_args.kwargs
        self.assertEqual(
            publish_kwargs["TopicArn"],
            "arn:aws:sns:us-east-1:123456789012:topic",
        )
        self.assertEqual(publish_kwargs["Subject"], "Image Moderation Completed")
        payload = json.loads(publish_kwargs["Message"])
        self.assertEqual(payload["event_type"], "SUCCESS")
        self.assertEqual(payload["image_id"], "a")
        self.assertEqual(payload["s3_key"], "uploads/a.jpg")
        self.assertEqual(payload["status"], "unsafe")
        self.assertTrue(payload["unsafe_detected"])
        self.assertEqual(payload["labels_count"], 1)

    def test_download_image_reads_s3_body(self) -> None:
        body = SimpleNamespace(read=lambda: b"img-bytes")
        with patch.object(
            orchestrator_services.s3, "get_object", return_value={"Body": body}
        ) as mock_get:
            result = orchestrator_services.download_image("bucket", "uploads/a.jpg")

        self.assertEqual(result, b"img-bytes")
        mock_get.assert_called_once_with(Bucket="bucket", Key="uploads/a.jpg")

    def test_delete_invalid_upload_calls_s3_delete(self) -> None:
        with patch.object(orchestrator_services.s3, "delete_object") as mock_delete:
            orchestrator_services.delete_invalid_upload("bucket", "uploads/a.jpg")

        mock_delete.assert_called_once_with(Bucket="bucket", Key="uploads/a.jpg")

    def test_validate_image_invalid_file_raises(self) -> None:
        with patch.object(orchestrator_services.Image, "open", side_effect=Exception):
            with self.assertRaises(orchestrator_services.APPError) as ctx:
                orchestrator_services.validate_image(b"not-an-image")

        self.assertEqual(ctx.exception.code, "INVALID_IMAGE_FILE")

    def test_validate_image_unsupported_type_raises(self) -> None:
        fake_image = SimpleNamespace(format="GIF")
        with patch.object(orchestrator_services.Image, "open", return_value=fake_image):
            with self.assertRaises(orchestrator_services.APPError) as ctx:
                orchestrator_services.validate_image(b"gif-bytes")

        self.assertEqual(ctx.exception.code, "UNSUPPORTED_IMAGE_TYPE")

    def test_validate_image_supported_type_returns_lowercase(self) -> None:
        fake_image = SimpleNamespace(format="JPEG")
        with patch.object(orchestrator_services.Image, "open", return_value=fake_image):
            result = orchestrator_services.validate_image(b"jpeg-bytes")

        self.assertEqual(result, "jpeg")

    def test_generate_image_hash_is_deterministic(self) -> None:
        data = b"abc"
        expected = hashlib.sha256(data).hexdigest()

        self.assertEqual(orchestrator_services.generate_image_hash(data), expected)

    def test_find_existing_image_returns_none_when_missing(self) -> None:
        with patch.object(
            orchestrator_services.table, "query", return_value={"Items": []}
        ) as mock_query:
            result = orchestrator_services.find_existing_image("hash-1")

        self.assertIsNone(result)
        self.assertEqual(mock_query.call_args.kwargs["IndexName"], "image_hash")
        self.assertEqual(mock_query.call_args.kwargs["Limit"], 1)

    def test_find_existing_image_returns_first_item(self) -> None:
        expected = {"image_id": "img-1", "status": "safe"}
        with patch.object(
            orchestrator_services.table,
            "query",
            return_value={"Items": [expected, {"image_id": "img-2"}]},
        ):
            result = orchestrator_services.find_existing_image("hash-1")

        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
