import os

import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime

from .identity_service import extract_image_id_from_s3_key

TABLE_NAME = os.environ["TABLE_NAME"]

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)  # type: ignore


def store_moderation_result(
    moderation_labels: list,
    object_key: str,
    image_hash: str,
    extracted_text: str | None = None,
    text_insights: dict | None = None,
):

    image_id = extract_image_id_from_s3_key(object_key)

    unsafe_detected = len(moderation_labels) > 0
    status = "unsafe" if unsafe_detected else "safe"

    item = {
        "imageId": image_id,
        "image_hash": image_hash,
        "s3_key": object_key,
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "unsafe_detected": unsafe_detected,
        "moderation_labels": moderation_labels,
    }

    if extracted_text:
        item["extracted_text"] = extracted_text

    if text_insights:
        item["text_insights"] = text_insights

    table.put_item(Item=item)


def find_existing_image(image_hash: str):

    dynamodb_response = table.query(
        IndexName="imageHash-index",
        KeyConditionExpression=Key("imageHash").eq(image_hash),
        Limit=1,
    )

    items = dynamodb_response.get("Items", [])

    if not items:
        return None

    return items[0]
