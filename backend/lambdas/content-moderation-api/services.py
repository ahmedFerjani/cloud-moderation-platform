import boto3
import os
import uuid
from common.responses import api_response
from common.logger import log
from common.exceptions import APPError
from constants import ALLOWED_CONTENT_TYPES, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

BUCKET_NAME = os.environ["BUCKET_NAME"]
TABLE_NAME = os.environ["TABLE_NAME"]

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)  # type: ignore


def generate_upload_url(body: dict) -> dict:

    content_type = body.get("content_type")

    if not content_type:
        raise APPError("MISSING_CONTENT_TYPE", "Missing content_type", 400)

    if content_type not in ALLOWED_CONTENT_TYPES:
        raise APPError("UNSUPPORTED_CONTENT_TYPE", "Unsupported content type", 400)

    extension = "jpg" if content_type == "image/jpeg" else "png"

    image_id = str(uuid.uuid4())
    object_key = f"uploads/{image_id}.{extension}"

    upload_url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={"Bucket": BUCKET_NAME, "Key": object_key, "ContentType": content_type},
        ExpiresIn=300,
    )

    log(
        "INFO",
        "Presigned upload URL generated",
        {"image_id": image_id, "object_key": object_key, "content_type": content_type},
    )

    return api_response(
        200,
        {
            "upload_url": upload_url,
            "image_id": image_id,
            "object_key": object_key,
            "expires_in": 300,
        },
    )


def get_moderation_result(image_id: str) -> dict:

    dynamodb_response = table.get_item(Key={"image_id": image_id})

    item = dynamodb_response.get("Item")

    if not item:

        raise APPError(
            "MODERATION_RESULT_NOT_FOUND", "Moderation result not found", 404
        )

    return api_response(200, item)


def get_moderation_results(limit: int) -> dict:

    dynamodb_response = table.scan(Limit=limit)

    return api_response(
        200,
        {
            "items": dynamodb_response.get("Items", []),
            "count": dynamodb_response.get("Count", 0),
            "last_evaluated_key": dynamodb_response.get("LastEvaluatedKey"),
        },
    )


def parse_limit(params: dict) -> int:

    try:
        limit = int(params.get("limit") or DEFAULT_PAGE_SIZE)

    except ValueError:

        raise APPError("INVALID_LIMIT", "Limit must be a valid integer", 400)

    return min(limit, MAX_PAGE_SIZE)
