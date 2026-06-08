from decimal import Decimal
from typing import Any, cast
from unittest.mock import patch

from _integration_test_setup import (
    FakeComprehendClient,
    FakeRekognitionClient,
    FakeS3Client,
    FakeSNSClient,
    FakeTable,
    FakeTextractClient,
    load_orchestrator_stack,
    orchestrator_runtime_event,
    runtime_context,
)


def _configure_orchestrator_service_doubles(
    service_module: Any,
    *,
    s3_client,
    rekognition_client,
    textract_client,
    comprehend_client,
    sns_client,
    table,
    sns_topic_arn: str | None = None,
) -> None:
    # Keep package-level references for existing test assertions.
    service_module.s3 = s3_client
    service_module.rekognition = rekognition_client
    service_module.textract = textract_client
    service_module.comprehend = comprehend_client
    service_module.sns = sns_client
    service_module.table = table
    service_module.SNS_SUCCESS_TOPIC_ARN = sns_topic_arn

    # Wire concrete split modules used by orchestrator runtime functions.
    service_module.storage_service.s3 = s3_client
    service_module.image_labeling_service.rekognition = rekognition_client
    service_module.image_labeling_service.textract = textract_client
    service_module.text_insights_service.comprehend = comprehend_client
    service_module.notification_service.sns = sns_client
    service_module.notification_service.SNS_SUCCESS_TOPIC_ARN = sns_topic_arn
    service_module.repository_service.table = table


# Verifies a valid image is persisted as safe and emits the success notification payload.
def test_orchestrator_handler_processes_safe_image_end_to_end() -> None:
    services, _processor, handler = load_orchestrator_stack()
    service_module = cast(Any, services)
    fake_s3 = FakeS3Client()
    fake_rekognition = FakeRekognitionClient(labels=[])
    fake_textract = FakeTextractClient(blocks=[])
    fake_comprehend = FakeComprehendClient()
    fake_sns = FakeSNSClient()
    fake_table = FakeTable()
    _configure_orchestrator_service_doubles(
        service_module,
        s3_client=fake_s3,
        rekognition_client=fake_rekognition,
        textract_client=fake_textract,
        comprehend_client=fake_comprehend,
        sns_client=fake_sns,
        table=fake_table,
        sns_topic_arn="arn:aws:sns:us-east-1:123456789012:test-topic",
    )

    event = orchestrator_runtime_event()
    context = runtime_context("req-orchestrator")

    with patch.object(handler, "capture_sample_event"):
        handler.lambda_handler(event, context)

    assert len(fake_table.put_items) == 1
    stored_item = fake_table.put_items[0]
    assert stored_item["status"] == "safe"
    assert stored_item["s3_key"] == "uploads/sample-image.jpg"
    assert "extracted_text" not in stored_item
    assert len(service_module.sns.published_messages) == 1
    notification = service_module.sns.last_message_body()
    assert notification["event_type"] == "SUCCESS"
    assert notification["status"] == "safe"
    assert not notification["unsafe_detected"]


# Verifies unreadable uploads are deleted and do not create downstream records or notifications.
def test_orchestrator_handler_deletes_invalid_upload_end_to_end() -> None:
    services, _processor, handler = load_orchestrator_stack()
    service_module = cast(Any, services)
    fake_s3 = FakeS3Client(image_bytes=b"not-an-image")
    fake_rekognition = FakeRekognitionClient(labels=[])
    fake_textract = FakeTextractClient(blocks=[])
    fake_comprehend = FakeComprehendClient()
    fake_sns = FakeSNSClient()
    fake_table = FakeTable()
    _configure_orchestrator_service_doubles(
        service_module,
        s3_client=fake_s3,
        rekognition_client=fake_rekognition,
        textract_client=fake_textract,
        comprehend_client=fake_comprehend,
        sns_client=fake_sns,
        table=fake_table,
    )

    event = orchestrator_runtime_event()
    context = runtime_context("req-invalid")

    with patch.object(handler, "capture_sample_event"):
        handler.lambda_handler(event, context)

    assert fake_s3.deleted_objects == [("<normalized-bucket>", "uploads/sample-image.jpg")]
    assert len(service_module.table.put_items) == 0
    assert len(service_module.sns.published_messages) == 0


# Verifies flagged moderation labels are persisted and surfaced as an unsafe notification.
def test_orchestrator_handler_processes_unsafe_image_end_to_end() -> None:
    services, _processor, handler = load_orchestrator_stack()
    service_module = cast(Any, services)
    fake_s3 = FakeS3Client()
    fake_rekognition = FakeRekognitionClient(
        labels=[
            {
                "Name": "Explicit Nudity",
                "Confidence": 99.1,
                "ParentName": "Nudity",
            }
        ]
    )
    fake_textract = FakeTextractClient(
        blocks=[{"BlockType": "LINE", "Text": "Extracted warning text"}]
    )
    fake_comprehend = FakeComprehendClient(
        sentiment="NEGATIVE",
        sentiment_scores={
            "Positive": 0.01,
            "Negative": 0.9,
            "Neutral": 0.07,
            "Mixed": 0.02,
        },
        pii_entities=[{"Type": "NAME", "Score": 0.95}],
        toxic_labels=[{"Name": "INSULT", "Score": 0.83}],
    )
    fake_sns = FakeSNSClient()
    fake_table = FakeTable()
    _configure_orchestrator_service_doubles(
        service_module,
        s3_client=fake_s3,
        rekognition_client=fake_rekognition,
        textract_client=fake_textract,
        comprehend_client=fake_comprehend,
        sns_client=fake_sns,
        table=fake_table,
        sns_topic_arn="arn:aws:sns:us-east-1:123456789012:test-topic",
    )

    with patch.object(handler, "capture_sample_event"):
        handler.lambda_handler(orchestrator_runtime_event(), runtime_context("req-unsafe"))

    assert len(fake_table.put_items) == 1
    stored_item = fake_table.put_items[0]
    assert stored_item["status"] == "unsafe"
    assert stored_item["unsafe_detected"]
    assert stored_item["extracted_text"] == "Extracted warning text"
    assert stored_item["text_insights"]["language_code"] == "en"
    assert stored_item["text_insights"]["sentiment"] == "NEGATIVE"
    assert stored_item["text_insights"]["toxicity_detected"]
    assert stored_item["text_insights"]["max_toxicity_score"] == Decimal("0.83")
    assert stored_item["text_insights"]["pii_entities_count"] == 1
    assert stored_item["text_insights"]["pii_entity_types"] == ["NAME"]
    assert len(stored_item["moderation_labels"]) == 1
    assert stored_item["moderation_labels"][0]["Name"] == "Explicit Nudity"
    assert len(service_module.sns.published_messages) == 1
    notification = service_module.sns.last_message_body()
    assert notification["status"] == "unsafe"
    assert notification["unsafe_detected"]
    assert notification["labels_count"] == 1


# Checks duplicate uploads are deleted and skipped.
def test_orchestrator_handler_skips_duplicate_image_end_to_end() -> None:
    services, _processor, handler = load_orchestrator_stack()
    service_module = cast(Any, services)
    fake_s3 = FakeS3Client()
    fake_rekognition = FakeRekognitionClient(labels=[])
    fake_textract = FakeTextractClient(blocks=[])
    fake_comprehend = FakeComprehendClient()
    fake_sns = FakeSNSClient()
    fake_table = FakeTable(
        existing_item={
            "image_id": "existing-image",
            "status": "safe",
            "image_hash": "ec4c891067050ba7b2f28c818666200e695328857bf52060d5140a707858de5b",
        }
    )
    _configure_orchestrator_service_doubles(
        service_module,
        s3_client=fake_s3,
        rekognition_client=fake_rekognition,
        textract_client=fake_textract,
        comprehend_client=fake_comprehend,
        sns_client=fake_sns,
        table=fake_table,
    )

    event = orchestrator_runtime_event()

    with patch.object(handler, "capture_sample_event"):
        handler.lambda_handler(event, runtime_context("req-duplicate"))

    assert len(service_module.table.put_items) == 0
    assert len(service_module.sns.published_messages) == 0
    assert service_module.s3.deleted_objects == [
        ("<normalized-bucket>", "uploads/sample-image.jpg")
    ]
