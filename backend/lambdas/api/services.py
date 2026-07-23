import boto3
import os
import uuid
from common.responses import api_response
from common.logger import log
from common.exceptions import APPError
from constants import (
    MAX_UPLOAD_FILE_SIZE_BYTES,
    UPLOAD_URL_EXPIRES_IN_SECONDS,
)
from validation import normalize_content_types

BUCKET_NAME = os.environ["BUCKET_NAME"]
TABLE_NAME = os.environ["TABLE_NAME"]

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)  # type: ignore


def generate_upload_url(body: dict, user_id: str) -> dict:

    content_types = normalize_content_types(body)

    uploads = [create_presigned_upload(content_type, user_id) for content_type in content_types]

    return api_response(
        200,
        {
            "uploads": uploads,
            "count": len(uploads),
            "expires_in": UPLOAD_URL_EXPIRES_IN_SECONDS,
            "max_upload_size_bytes": MAX_UPLOAD_FILE_SIZE_BYTES,
        },
    )


def create_presigned_upload(content_type: str, user_id: str) -> dict:
    extension = "jpg" if content_type == "image/jpeg" else "png"

    image_id = str(uuid.uuid4())
    object_key = f"uploads/{user_id}/{image_id}.{extension}"

    presigned_post = s3.generate_presigned_post(
        Bucket=BUCKET_NAME,
        Key=object_key,
        Fields={"Content-Type": content_type},
        Conditions=[
            ["starts-with", "$key", f"uploads/{user_id}/"],
            {"Content-Type": content_type},
            ["content-length-range", 1, MAX_UPLOAD_FILE_SIZE_BYTES],
        ],
        ExpiresIn=UPLOAD_URL_EXPIRES_IN_SECONDS,
    )

    log(
        "INFO",
        "Presigned upload POST generated",
        {"image_id": image_id, "object_key": object_key, "content_type": content_type},
    )

    return {
        "upload_url": presigned_post["url"],
        "upload_method": "POST",
        "upload_form_fields": presigned_post["fields"],
        "image_id": image_id,
        "object_key": object_key,
        "content_type": content_type,
        "expires_in": UPLOAD_URL_EXPIRES_IN_SECONDS,
        "max_upload_size_bytes": MAX_UPLOAD_FILE_SIZE_BYTES,
    }


def get_moderation_result(image_id: str) -> dict:

    dynamodb_response = table.get_item(Key={"image_id": image_id})

    item = dynamodb_response.get("Item")

    if not item:

        raise APPError("MODERATION_RESULT_NOT_FOUND", "Moderation result not found", 404)

    return api_response(200, item)


def get_moderation_results(limit: int, last_evaluated_key: dict[str, str] | None = None) -> dict:
    scan_params: dict[str, int | dict[str, str]] = {
        "Limit": limit,
    }

    if last_evaluated_key:
        scan_params["ExclusiveStartKey"] = last_evaluated_key

    dynamodb_response = table.scan(**scan_params)

    return api_response(
        200,
        {
            "items": dynamodb_response.get("Items", []),
            "count": dynamodb_response.get("Count", 0),
            "last_evaluated_key": dynamodb_response.get("LastEvaluatedKey"),
        },
    )
