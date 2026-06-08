import json
from unittest.mock import patch

from _orchestrator_test_setup import orchestrator_services

notification_service = orchestrator_services.notification_service


# Verifies success notifications are skipped when topic configuration is absent.
def test_send_success_notification_skips_without_topic() -> None:
    with (
        patch.object(notification_service, "SNS_SUCCESS_TOPIC_ARN", None),
        patch.object(notification_service.sns, "publish") as mock_publish,
    ):
        notification_service.send_success_notification("uploads/a.jpg", [])

    mock_publish.assert_not_called()


# Verifies success notifications include the expected envelope and moderation summary payload.
def test_send_success_notification_publishes_payload() -> None:
    with (
        patch.object(
            notification_service,
            "SNS_SUCCESS_TOPIC_ARN",
            "arn:aws:sns:us-east-1:123456789012:topic",
        ),
        patch.object(notification_service.sns, "publish") as mock_publish,
    ):
        notification_service.send_success_notification("uploads/a.jpg", [{"Name": "Violence"}])

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
