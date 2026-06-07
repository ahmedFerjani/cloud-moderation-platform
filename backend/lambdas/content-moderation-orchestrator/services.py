import json
import boto3
import os
import hashlib

from io import BytesIO
from PIL import Image
from datetime import datetime
from decimal import Decimal
from boto3.dynamodb.conditions import Key

from common.exceptions import APPError
from constants import ALLOWED_IMAGE_TYPES, MIN_CONFIDENCE, MAX_UPLOAD_SIZE_BYTES

TABLE_NAME = os.environ["TABLE_NAME"]
SNS_SUCCESS_TOPIC_ARN = os.environ.get("SNS_SUCCESS_TOPIC_ARN")

rekognition = boto3.client("rekognition")
textract = boto3.client("textract")
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")
table = dynamodb.Table(TABLE_NAME)  # type: ignore


def extract_image_id_from_s3_key(object_key: str) -> str:

    filename = object_key.rsplit("/", 1)[-1]
    image_id, _ = os.path.splitext(filename)

    return image_id


def detect_moderation_labels(bucket_name: str, object_key: str) -> list:

    image = {"S3Object": {"Bucket": bucket_name, "Name": object_key}}

    rekognition_response = rekognition.detect_moderation_labels(
        Image=image, MinConfidence=MIN_CONFIDENCE
    )

    moderation_labels = [
        {
            "Name": label["Name"],
            "Confidence": Decimal(str(label["Confidence"])),
            "ParentName": label.get("ParentName"),
        }
        for label in rekognition_response["ModerationLabels"]
    ]

    return moderation_labels


def extract_text_from_image(bucket_name: str, object_key: str) -> str | None:

    textract_response = textract.detect_document_text(
        Document={"S3Object": {"Bucket": bucket_name, "Name": object_key}}
    )

    extracted_lines = [
        block["Text"].strip()
        for block in textract_response.get("Blocks", [])
        if block.get("BlockType") == "LINE" and block.get("Text", "").strip()
    ]

    if not extracted_lines:
        return None

    return "\n".join(extracted_lines)


def store_moderation_result(
    moderation_labels: list,
    object_key: str,
    image_hash: str,
    extracted_text: str | None = None,
):

    image_id = extract_image_id_from_s3_key(object_key)

    unsafe_detected = len(moderation_labels) > 0
    status = "unsafe" if unsafe_detected else "safe"

    item = {
        "image_id": image_id,
        "s3_key": object_key,
        "image_hash": image_hash,
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "unsafe_detected": unsafe_detected,
        "moderation_labels": moderation_labels,
    }

    if extracted_text:
        item["extracted_text"] = extracted_text

    table.put_item(Item=item)


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


def download_image(bucket_name: str, object_key: str) -> bytes:

    s3_response = s3.get_object(Bucket=bucket_name, Key=object_key)

    return s3_response["Body"].read()


def validate_upload_size(object_size: int):

    if object_size <= 0:
        raise APPError("INVALID_OBJECT_SIZE", "Uploaded object is empty", 400)

    if object_size > MAX_UPLOAD_SIZE_BYTES:
        raise APPError(
            "UPLOAD_TOO_LARGE",
            f"Uploaded object exceeds max size of {MAX_UPLOAD_SIZE_BYTES} bytes",
            400,
        )


def delete_invalid_upload(bucket_name: str, object_key: str):

    s3.delete_object(Bucket=bucket_name, Key=object_key)


def validate_image(image_data: bytes) -> str:

    try:

        image = Image.open(BytesIO(image_data))

        image_type = (image.format or "").lower()

    except Exception:

        raise APPError("INVALID_IMAGE_FILE", "Invalid image file", 400)

    if image_type not in ALLOWED_IMAGE_TYPES:

        raise APPError("UNSUPPORTED_IMAGE_TYPE", "Unsupported image type", 400)

    return image_type


def generate_image_hash(image_data: bytes) -> str:

    return hashlib.sha256(image_data).hexdigest()


def find_existing_image(image_hash: str):

    dynamodb_response = table.query(
        IndexName="image_hash",
        KeyConditionExpression=Key("image_hash").eq(image_hash),
        Limit=1,
    )

    items = dynamodb_response.get("Items", [])

    if not items:
        return None

    return items[0]
