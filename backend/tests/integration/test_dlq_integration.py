import unittest
from typing import Any, cast
from unittest.mock import patch

from _integration_test_setup import (
    FakeSNSClient,
    FakeTable,
    dlq_runtime_event,
    load_dlq_stack,
    runtime_context,
)


class DlqIntegrationTests(unittest.TestCase):
    # Verifies DLQ messages are persisted as failures and emit the configured notification payload.
    def test_dlq_handler_stores_failure_and_sends_notification_end_to_end(self) -> None:
        services, _processor, handler = load_dlq_stack()
        service_module = cast(Any, services)
        fake_table = FakeTable()
        fake_sns = FakeSNSClient()
        service_module.table = fake_table
        service_module.sns = fake_sns
        service_module.SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:123456789012:test-topic"

        event = dlq_runtime_event(error="rekognition_timeout", image_hash="abc123")

        with patch.object(handler, "capture_sample_event"):
            handler.lambda_handler(event, runtime_context("req-dlq"))

        self.assertEqual(len(fake_table.put_items), 1)
        stored_item = fake_table.put_items[0]
        self.assertEqual(stored_item["image_id"], "sample-image")
        self.assertEqual(stored_item["status"], "failed")
        self.assertEqual(stored_item["failure_reason"], "rekognition_timeout")
        self.assertEqual(stored_item["image_hash"], "abc123")

        self.assertEqual(len(fake_sns.published_messages), 1)
        message = fake_sns.last_message_body()
        self.assertEqual(message["image_id"], "sample-image")
        self.assertEqual(message["s3_key"], "uploads/sample-image.jpg")
        self.assertEqual(message["reason"], "rekognition_timeout")

    # Verifies failure persistence still happens when DLQ notifications are intentionally disabled.
    def test_dlq_handler_stores_failure_without_notification_when_topic_missing(self) -> None:
        services, _processor, handler = load_dlq_stack()
        service_module = cast(Any, services)
        fake_table = FakeTable()
        fake_sns = FakeSNSClient()
        service_module.table = fake_table
        service_module.sns = fake_sns
        service_module.SNS_TOPIC_ARN = None

        event = dlq_runtime_event(error="notification_disabled")

        with patch.object(handler, "capture_sample_event"):
            handler.lambda_handler(event, runtime_context("req-dlq-no-topic"))

        self.assertEqual(len(fake_table.put_items), 1)
        stored_item = fake_table.put_items[0]
        self.assertEqual(stored_item["status"], "failed")
        self.assertEqual(stored_item["failure_reason"], "notification_disabled")
        self.assertEqual(len(fake_sns.published_messages), 0)


if __name__ == "__main__":
    unittest.main()
