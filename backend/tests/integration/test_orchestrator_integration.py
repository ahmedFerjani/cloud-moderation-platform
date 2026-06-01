import unittest
from typing import Any, cast
from unittest.mock import patch

from _integration_test_setup import (
    FakeRekognitionClient,
    FakeS3Client,
    FakeSNSClient,
    FakeTable,
    load_orchestrator_stack,
    orchestrator_runtime_event,
    runtime_context,
)


class OrchestratorIntegrationTests(unittest.TestCase):
    # Verifies a valid image is persisted as safe and emits the success notification payload.
    def test_orchestrator_handler_processes_safe_image_end_to_end(self) -> None:
        services, _processor, handler = load_orchestrator_stack()
        service_module = cast(Any, services)
        service_module.s3 = FakeS3Client()
        service_module.rekognition = FakeRekognitionClient(labels=[])
        service_module.sns = FakeSNSClient()
        service_module.SNS_SUCCESS_TOPIC_ARN = "arn:aws:sns:us-east-1:123456789012:test-topic"
        fake_table = FakeTable()
        service_module.table = fake_table

        event = orchestrator_runtime_event()
        context = runtime_context("req-orchestrator")

        with patch.object(handler, "capture_sample_event"):
            handler.lambda_handler(event, context)

        self.assertEqual(len(fake_table.put_items), 1)
        stored_item = fake_table.put_items[0]
        self.assertEqual(stored_item["status"], "safe")
        self.assertEqual(stored_item["s3_key"], "uploads/sample-image.jpg")
        self.assertEqual(len(service_module.sns.published_messages), 1)
        notification = service_module.sns.last_message_body()
        self.assertEqual(notification["event_type"], "SUCCESS")
        self.assertEqual(notification["status"], "safe")
        self.assertFalse(notification["unsafe_detected"])

    # Verifies unreadable uploads are deleted and do not create downstream records or notifications.
    def test_orchestrator_handler_deletes_invalid_upload_end_to_end(self) -> None:
        services, _processor, handler = load_orchestrator_stack()
        service_module = cast(Any, services)
        fake_s3 = FakeS3Client(image_bytes=b"not-an-image")
        service_module.s3 = fake_s3
        service_module.rekognition = FakeRekognitionClient(labels=[])
        service_module.sns = FakeSNSClient()
        service_module.table = FakeTable()

        event = orchestrator_runtime_event()
        context = runtime_context("req-invalid")

        with patch.object(handler, "capture_sample_event"):
            handler.lambda_handler(event, context)

        self.assertEqual(
            fake_s3.deleted_objects, [("<normalized-bucket>", "uploads/sample-image.jpg")]
        )
        self.assertEqual(len(service_module.table.put_items), 0)
        self.assertEqual(len(service_module.sns.published_messages), 0)

    # Verifies flagged moderation labels are persisted and surfaced as an unsafe notification.
    def test_orchestrator_handler_processes_unsafe_image_end_to_end(self) -> None:
        services, _processor, handler = load_orchestrator_stack()
        service_module = cast(Any, services)
        service_module.s3 = FakeS3Client()
        service_module.rekognition = FakeRekognitionClient(
            labels=[
                {
                    "Name": "Explicit Nudity",
                    "Confidence": 99.1,
                    "ParentName": "Nudity",
                }
            ]
        )
        service_module.sns = FakeSNSClient()
        service_module.SNS_SUCCESS_TOPIC_ARN = "arn:aws:sns:us-east-1:123456789012:test-topic"
        fake_table = FakeTable()
        service_module.table = fake_table

        with patch.object(handler, "capture_sample_event"):
            handler.lambda_handler(orchestrator_runtime_event(), runtime_context("req-unsafe"))

        self.assertEqual(len(fake_table.put_items), 1)
        stored_item = fake_table.put_items[0]
        self.assertEqual(stored_item["status"], "unsafe")
        self.assertTrue(stored_item["unsafe_detected"])
        self.assertEqual(len(stored_item["moderation_labels"]), 1)
        self.assertEqual(stored_item["moderation_labels"][0]["Name"], "Explicit Nudity")
        self.assertEqual(len(service_module.sns.published_messages), 1)
        notification = service_module.sns.last_message_body()
        self.assertEqual(notification["status"], "unsafe")
        self.assertTrue(notification["unsafe_detected"])
        self.assertEqual(notification["labels_count"], 1)

    # Checks duplicate uploads are skipped.
    def test_orchestrator_handler_skips_duplicate_image_end_to_end(self) -> None:
        services, _processor, handler = load_orchestrator_stack()
        service_module = cast(Any, services)
        service_module.s3 = FakeS3Client()
        service_module.rekognition = FakeRekognitionClient(labels=[])
        service_module.sns = FakeSNSClient()
        service_module.table = FakeTable(
            existing_item={
                "image_id": "existing-image",
                "status": "safe",
                "image_hash": "ec4c891067050ba7b2f28c818666200e695328857bf52060d5140a707858de5b",
            }
        )

        event = orchestrator_runtime_event()

        with patch.object(handler, "capture_sample_event"):
            handler.lambda_handler(event, runtime_context("req-duplicate"))

        self.assertEqual(len(service_module.table.put_items), 0)
        self.assertEqual(len(service_module.sns.published_messages), 0)
        self.assertEqual(service_module.s3.deleted_objects, [])


if __name__ == "__main__":
    unittest.main()
