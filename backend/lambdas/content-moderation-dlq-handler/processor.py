import json
import boto3
import os

from common.logger import log
from services import send_notification, store_failure

TABLE_NAME = os.environ["TABLE_NAME"]
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")

dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")
table = dynamodb.Table(TABLE_NAME)  # type: ignore


def extract_dlq_messages(event):

    for record in event["Records"]:
        yield json.loads(record["body"])


def process_dlq_event(event):

    messages = list(extract_dlq_messages(event))
    total_records = len(messages)
    success_records = 0

    log("INFO", "DLQ processing batch started", {"total_records": total_records})

    for message in messages:

        image_id = message.get("image_id")
        object_key = message.get("s3_key")

        ctx = {
            "image_id": image_id,
            "object_key": object_key,
        }

        log("INFO", "Processing DLQ message START", ctx)

        store_failure(message)

        log("INFO", "Failure stored in DynamoDB", ctx)

        send_notification(message)

        log("INFO", "Failure SNS notification sent", ctx)

        success_records += 1

        log("INFO", "Processing DLQ message END", ctx)

    log(
        "INFO",
        "DLQ batch processing END",
        {"total_records": total_records, "success_records": success_records},
    )
