from . import notification_service as _notification_service
from . import (
    identity_service,
    image_labeling_service,
    notification_service,
    repository_service,
    storage_service,
    text_insights_service,
)
from .image_labeling_service import detect_moderation_labels, extract_text_from_image, rekognition
from .identity_service import extract_image_id_from_s3_key, generate_image_hash
from .repository_service import find_existing_image, store_moderation_result, table
from .storage_service import delete_uploaded_image, download_image, s3
from .text_insights_service import analyze_extracted_text, comprehend

sns = _notification_service.sns
SNS_SUCCESS_TOPIC_ARN = _notification_service.SNS_SUCCESS_TOPIC_ARN


def send_success_notification(object_key: str, moderation_labels: list):
    # Keep package-level topic overrides (used in tests) in sync with notification module state.
    _notification_service.SNS_SUCCESS_TOPIC_ARN = SNS_SUCCESS_TOPIC_ARN
    return _notification_service.send_success_notification(object_key, moderation_labels)


__all__ = [
    "analyze_extracted_text",
    "delete_uploaded_image",
    "download_image",
    "extract_image_id_from_s3_key",
    "find_existing_image",
    "generate_image_hash",
    "send_success_notification",
    "store_moderation_result",
    "detect_moderation_labels",
    "extract_text_from_image",
    "SNS_SUCCESS_TOPIC_ARN",
    "comprehend",
    "rekognition",
    "s3",
    "sns",
    "table",
    "identity_service",
    "image_labeling_service",
    "notification_service",
    "repository_service",
    "storage_service",
    "text_insights_service",
]
