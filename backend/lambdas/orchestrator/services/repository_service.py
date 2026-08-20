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
    original_name: str | None = None,
):

    image_id = extract_image_id_from_s3_key(object_key)

    text_toxicity_detected = bool(text_insights and text_insights.get("toxicity_detected"))
    unsafe_detected = len(moderation_labels) > 0 or text_toxicity_detected
    status = "unsafe" if unsafe_detected else "safe"

    item = {
        "image_id": image_id,
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

    if original_name:
        item["original_name"] = original_name

    table.put_item(Item=item)

    return status


def find_existing_image(image_hash: str):

    dynamodb_response = table.query(
        IndexName="image_hash_index",
        KeyConditionExpression=Key("image_hash").eq(image_hash),
        Limit=1,
    )

    items = dynamodb_response.get("Items", [])

    if not items:
        return None

    return items[0]
