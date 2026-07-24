import json

from common.logger import log
from common.exceptions import APPError
from services import (
    analyze_extracted_text,
    delete_uploaded_image,
    detect_moderation_labels,
    extract_text_from_image,
    download_image,
    extract_image_id_from_s3_key,
    extract_user_id_from_s3_key,
    store_moderation_result,
    generate_image_hash,
    find_existing_image,
    notify_user,
)
from validation import validate_image, validate_upload_size

STATUS_SUCCESS = "success"
STATUS_DUPLICATE = "duplicate"
STATUS_REJECTED = "rejected"


def _extract_s3_records(event):

    for sqs_record in event["Records"]:

        sqs_record_body = json.loads(sqs_record["body"])

        for s3_record in sqs_record_body["Records"]:
            yield s3_record


def _build_context(bucket_name, object_key):

    return {
        "bucket_name": bucket_name,
        "object_key": object_key,
        "image_id": extract_image_id_from_s3_key(object_key),
        "user_id": extract_user_id_from_s3_key(object_key),
    }


def _handle_existing_item(existing_item, bucket_name, object_key, ctx):

    if not existing_item:
        return False

    if existing_item["status"] != "failed":

        delete_uploaded_image(bucket_name, object_key)

        log(
            "INFO",
            "Duplicate image detected and deleted",
            {
                **ctx,
                "existing_image_id": existing_item["image_id"],
            },
        )

        return True

    existing_s3_key = existing_item.get("s3_key")
    if existing_s3_key:
        delete_uploaded_image(bucket_name, existing_s3_key)

    log(
        "INFO",
        "Existing failed item found; deleting previous object and continuing",
        {
            **ctx,
            "existing_image_id": existing_item.get("image_id"),
            "existing_s3_key": existing_s3_key,
        },
    )

    return False


def _extract_text_and_insights(bucket_name, object_key, ctx):

    extracted_text = extract_text_from_image(bucket_name, object_key)
    text_insights = None

    if extracted_text:
        log("INFO", "Textract completed", {**ctx, "text_length": len(extracted_text)})

        text_insights = analyze_extracted_text(extracted_text)
        log(
            "INFO",
            "Comprehend completed",
            {
                **ctx,
                "language_code": text_insights.get("language_code"),
                "sentiment": text_insights.get("sentiment"),
                "toxicity_detected": text_insights.get("toxicity_detected"),
                "max_toxicity_score": text_insights.get("max_toxicity_score"),
                "toxicity_labels_count": len(text_insights.get("toxicity_labels", [])),
                "pii_entities_count": text_insights.get("pii_entities_count"),
            },
        )
    else:
        log("INFO", "Textract completed", {**ctx, "text_length": 0})

    return extracted_text, text_insights


def _process_single_record(s3_record):

    bucket_name = s3_record["s3"]["bucket"]["name"]
    object_key = s3_record["s3"]["object"]["key"]
    ctx = _build_context(bucket_name, object_key)

    log("INFO", "Processing image START", ctx)

    try:

        object_size = int(s3_record["s3"]["object"].get("size") or 0)
        validate_upload_size(object_size)

        image_data = download_image(bucket_name, object_key)

        log("INFO", "Image downloaded", {**ctx, "object_size": object_size})

        image_hash = generate_image_hash(image_data)

        log("INFO", "Image hash generated", {**ctx, "image_hash": image_hash})

        existing_item = find_existing_image(image_hash)

        if _handle_existing_item(existing_item, bucket_name, object_key, ctx):
            return STATUS_DUPLICATE

        image_type = validate_image(image_data)

        log("INFO", "Image validated", {**ctx, "image_type": image_type})

        moderation_labels = detect_moderation_labels(bucket_name, object_key)

        log(
            "INFO",
            "Rekognition completed",
            {**ctx, "labels_count": len(moderation_labels)},
        )

        extracted_text, text_insights = _extract_text_and_insights(bucket_name, object_key, ctx)

        store_moderation_result(
            moderation_labels,
            object_key,
            image_hash,
            extracted_text,
            text_insights,
        )

        log("INFO", "DynamoDB stored", ctx)

        notify_user(
            ctx["user_id"],
            {
                "type": "moderation_result",
                "status": STATUS_SUCCESS,
                "imageId": ctx["image_id"],
            },
        )

        return STATUS_SUCCESS

    except APPError as e:

        delete_uploaded_image(bucket_name, object_key)

        log(
            "WARN",
            f"Upload rejected and deleted: {e.message}",
            {
                **ctx,
                "code": e.code,
            },
        )

        notify_user(
            ctx["user_id"],
            {
                "type": "moderation_result",
                "status": STATUS_REJECTED,
                "imageId": ctx["image_id"],
                "reason": e.message,
            },
        )

        return STATUS_REJECTED


def process_moderation_event(event):

    s3_records = list(_extract_s3_records(event))

    counters = {
        STATUS_SUCCESS: 0,
        STATUS_DUPLICATE: 0,
        STATUS_REJECTED: 0,
    }
    total_records = len(s3_records)

    log("INFO", "Moderation batch started", {"total_records": total_records})

    for s3_record in s3_records:

        result = _process_single_record(s3_record)

        if result in counters:
            counters[result] += 1

    log(
        "INFO",
        "Moderation batch END",
        {"total_records": total_records, **counters},
    )
