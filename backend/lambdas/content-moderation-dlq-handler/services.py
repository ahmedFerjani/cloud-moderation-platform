import json
import boto3
import os

from datetime import datetime

TABLE_NAME = os.environ["TABLE_NAME"]
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")

dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")
table = dynamodb.Table(TABLE_NAME)  # type: ignore


def extract_image_id(message: dict) -> str:

    object_key = message.get("s3_key")

    if not object_key:
        return "unknown"

    return object_key.split("/")[-1]


def store_failure(message: dict):

    image_id = extract_image_id(message)

    table.put_item(
        Item={
            "image_id": image_id,
            "s3_key": message.get("s3_key"),
            "status": "failed",
            "failure_reason": message.get("error", "moved_to_dlq"),
            "timestamp": datetime.now().isoformat(),
        }
    )


def send_notification(message: dict):

    if not SNS_TOPIC_ARN:
        return

    image_id = extract_image_id(message)

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject="Image Moderation Failed (DLQ)",
        Message=json.dumps(
            {
                "image_id": image_id,
                "s3_key": message.get("s3_key"),
                "reason": message.get("error", "moved_to_dlq"),
            }
        ),
    )
