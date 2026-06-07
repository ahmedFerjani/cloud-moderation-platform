import json
import os

import boto3
from datetime import datetime

from .identity_service import extract_image_id_from_s3_key

SNS_SUCCESS_TOPIC_ARN = os.environ.get("SNS_SUCCESS_TOPIC_ARN")

sns = boto3.client("sns")


def send_success_notification(object_key: str, moderation_labels: list):

    if not SNS_SUCCESS_TOPIC_ARN:
        return

    image_id = extract_image_id_from_s3_key(object_key)
    unsafe_detected = len(moderation_labels) > 0

    sns.publish(
        TopicArn=SNS_SUCCESS_TOPIC_ARN,
        Subject="Image Moderation Completed",
        Message=json.dumps(
            {
                "event_type": "SUCCESS",
                "image_id": image_id,
                "s3_key": object_key,
                "status": "unsafe" if unsafe_detected else "safe",
                "unsafe_detected": unsafe_detected,
                "labels_count": len(moderation_labels),
                "timestamp": datetime.now().isoformat(),
            }
        ),
    )
