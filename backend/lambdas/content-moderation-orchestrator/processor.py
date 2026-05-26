import json
import boto3
import os

from common.logger import log
from services import (
    detect_moderation_labels,
    download_image,
    send_success_notification,
    store_moderation_result,
    validate_image,
    generate_image_hash,
    find_existing_image,
)

TABLE_NAME = os.environ["TABLE_NAME"]
SNS_SUCCESS_TOPIC_ARN = os.environ.get("SNS_SUCCESS_TOPIC_ARN")

rekognition = boto3.client("rekognition")
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")
table = dynamodb.Table(TABLE_NAME)  # type: ignore


def extract_s3_records(event):

    for sqs_record in event["Records"]:

        sqs_record_body = json.loads(sqs_record["body"])

        for s3_record in sqs_record_body["Records"]:
            yield s3_record


def process_moderation_event(event):

    s3_records = list(extract_s3_records(event))

    total_records = len(s3_records)
    success_records = 0

    log("INFO", "Moderation batch started", {"total_records": total_records})

    for s3_record in s3_records:

        bucket_name = s3_record["s3"]["bucket"]["name"]
        object_key = s3_record["s3"]["object"]["key"]

        ctx = {
            "bucket_name": bucket_name,
            "object_key": object_key,
            "image_id": object_key.split("/")[-1],
        }

        log("INFO", "Processing image START", ctx)

        image_data = download_image(bucket_name, object_key)

        log("INFO", "Image downloaded", ctx)

        image_hash = generate_image_hash(image_data)

        log("INFO", "Image hash generated", {**ctx, "image_hash": image_hash})

        existing_item = find_existing_image(image_hash)

        if existing_item and existing_item["status"] != "failed":

            log(
                "INFO",
                "Duplicate image detected",
                {**ctx, "existing_image_id": existing_item["image_id"]},
            )

            success_records += 1

            continue

        image_type = validate_image(image_data)

        log("INFO", "Image validated", {**ctx, "image_type": image_type})

        moderation_labels = detect_moderation_labels(bucket_name, object_key)

        log(
            "INFO",
            "Rekognition completed",
            {**ctx, "labels_count": len(moderation_labels)},
        )

        store_moderation_result(moderation_labels, object_key, image_hash)

        log("INFO", "DynamoDB stored", ctx)

        send_success_notification(object_key, moderation_labels)

        log("INFO", "SNS sent", ctx)

        success_records += 1

        log("INFO", "Processing image END", ctx)

    log(
        "INFO",
        "Moderation batch END",
        {"total_records": total_records, "success_records": success_records},
    )
