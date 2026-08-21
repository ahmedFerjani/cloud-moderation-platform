import boto3
import os
import uuid
from datetime import datetime, timezone
from botocore.exceptions import ClientError
from common.responses import api_response
from common.logger import log
from common.exceptions import APPError
from constants import (
    MAX_UPLOAD_FILE_SIZE_BYTES,
    UPLOAD_URL_EXPIRES_IN_SECONDS,
    VIEW_URL_EXPIRES_IN_SECONDS,
)
from validation import normalize_content_types, normalize_file_names

BUCKET_NAME = os.environ["BUCKET_NAME"]
TABLE_NAME = os.environ["TABLE_NAME"]

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)  # type: ignore


def _build_view_access(object_key: str, image_id: str) -> dict | None:
    issued_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": object_key},
            ExpiresIn=VIEW_URL_EXPIRES_IN_SECONDS,
        )
    except ClientError:
        log(
            "WARNING",
            "Unable to generate presigned image view URL",
            {"image_id": image_id, "object_key": object_key},
        )
        return None

    return {
        "url": url,
        "expires_in": VIEW_URL_EXPIRES_IN_SECONDS,
        "issued_at": issued_at,
    }


def _add_view_access(response_payload: dict, image_id: str) -> None:
    object_key = response_payload.get("s3_key")
    if not object_key:
        return

    view_access = _build_view_access(object_key, image_id)
    if view_access:
        response_payload["view_access"] = view_access


def _get_result_item_or_raise(image_id: str) -> dict:
    dynamodb_response = table.get_item(Key={"image_id": image_id})
    item = dynamodb_response.get("Item")

    if not item:
        raise APPError("MODERATION_RESULT_NOT_FOUND", "Moderation result not found", 404)

    return item


def get_moderation_result_view_url(image_id: str) -> dict:
    item = _get_result_item_or_raise(image_id)
    object_key = item.get("s3_key")

    if not object_key:
        raise APPError("VIEW_URL_NOT_AVAILABLE", "View URL not available for this image", 404)

    view_access = _build_view_access(object_key, image_id)
    if not view_access:
        raise APPError("VIEW_URL_NOT_AVAILABLE", "View URL not available for this image", 503)

    return api_response(200, {"image_id": image_id, "view_access": view_access})


def generate_upload_url(body: dict, user_id: str) -> dict:

    content_types = normalize_content_types(body)
    file_names = normalize_file_names(body, len(content_types))

    uploads = [
        create_presigned_upload(content_type, user_id, file_name)
        for content_type, file_name in zip(content_types, file_names)
    ]

    return api_response(
        200,
        {
            "uploads": uploads,
            "count": len(uploads),
            "expires_in": UPLOAD_URL_EXPIRES_IN_SECONDS,
            "max_upload_size_bytes": MAX_UPLOAD_FILE_SIZE_BYTES,
        },
    )


def create_presigned_upload(content_type: str, user_id: str, file_name: str | None = None) -> dict:
    extension = "jpg" if content_type == "image/jpeg" else "png"

    image_id = str(uuid.uuid4())
    object_key = f"uploads/{user_id}/{image_id}.{extension}"

    fields = {"Content-Type": content_type}
    conditions = [
        ["starts-with", "$key", f"uploads/{user_id}/"],
        {"Content-Type": content_type},
        ["content-length-range", 1, MAX_UPLOAD_FILE_SIZE_BYTES],
    ]

    if file_name:
        fields["x-amz-meta-original-filename"] = file_name
        conditions.append({"x-amz-meta-original-filename": file_name})

    presigned_post = s3.generate_presigned_post(
        Bucket=BUCKET_NAME,
        Key=object_key,
        Fields=fields,
        Conditions=conditions,
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
    item = _get_result_item_or_raise(image_id)

    response_payload = dict(item)
    _add_view_access(response_payload, image_id)

    return api_response(200, response_payload)


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
