import unittest
from unittest.mock import patch

from _dlq_test_setup import dlq_services


class DlqServicesTests(unittest.TestCase):
    def test_extract_image_id(self) -> None:
        self.assertEqual(dlq_services.extract_image_id({}), "unknown")
        self.assertEqual(
            dlq_services.extract_image_id({"s3_key": "uploads/abc-123.jpg"}), "abc-123"
        )

    def test_store_failure_omits_invalid_image_hash(self) -> None:
        with patch.object(dlq_services.table, "put_item") as mock_put:
            dlq_services.store_failure({"s3_key": "uploads/img-1.jpg", "image_hash": None})
            item = mock_put.call_args.kwargs["Item"]

        self.assertNotIn("image_hash", item)

    def test_store_failure_omits_whitespace_image_hash(self) -> None:
        with patch.object(dlq_services.table, "put_item") as mock_put:
            dlq_services.store_failure({"s3_key": "uploads/img-1.jpg", "image_hash": "   "})
            item = mock_put.call_args.kwargs["Item"]

        self.assertNotIn("image_hash", item)

    def test_store_failure_includes_valid_image_hash(self) -> None:
        with patch.object(dlq_services.table, "put_item") as mock_put:
            dlq_services.store_failure(
                {
                    "s3_key": "uploads/img-1.jpg",
                    "image_hash": "abc123",
                    "error": "failed",
                }
            )
            item = mock_put.call_args.kwargs["Item"]

        self.assertEqual(item["image_hash"], "abc123")
        self.assertEqual(item["failure_reason"], "failed")

    def test_store_failure_defaults_reason_when_missing(self) -> None:
        with patch.object(dlq_services.table, "put_item") as mock_put:
            dlq_services.store_failure({"s3_key": "uploads/img-1.jpg"})
            item = mock_put.call_args.kwargs["Item"]

        self.assertEqual(item["failure_reason"], "moved_to_dlq")

    def test_send_notification_skips_when_topic_missing(self) -> None:
        with patch.object(dlq_services, "SNS_TOPIC_ARN", None):
            with patch.object(dlq_services.sns, "publish") as mock_publish:
                dlq_services.send_notification({"s3_key": "uploads/img-1.jpg"})

        mock_publish.assert_not_called()

    def test_send_notification_publishes_when_topic_configured(self) -> None:
        with patch.object(dlq_services, "SNS_TOPIC_ARN", "arn:aws:sns:region:acct:topic"):
            with patch.object(dlq_services.sns, "publish") as mock_publish:
                dlq_services.send_notification(
                    {"s3_key": "uploads/img-1.jpg", "error": "moved_to_dlq"}
                )

        mock_publish.assert_called_once()


if __name__ == "__main__":
    unittest.main()
