import json

from common.logger import log
from common.exceptions import APPError
from services import (
    analyze_extracted_text,
    delete_invalid_upload,
    detect_moderation_labels,
    extract_text_from_image,
    download_image,
    extract_image_id_from_s3_key,
    send_success_notification,
    store_moderation_result,
    generate_image_hash,
    find_existing_image,
)
from validation import validate_image, validate_upload_size


def extract_s3_records(event):

    for sqs_record in event["Records"]:

        sqs_record_body = json.loads(sqs_record["body"])

        for s3_record in sqs_record_body["Records"]:
            yield s3_record


def process_moderation_event(event):

    s3_records = list(extract_s3_records(event))

    total_records = len(s3_records)
    success_records = 0
    duplicate_records = 0
    rejected_records = 0

    log("INFO", "Moderation batch started", {"total_records": total_records})

    for s3_record in s3_records:

        bucket_name = s3_record["s3"]["bucket"]["name"]
        object_key = s3_record["s3"]["object"]["key"]

        ctx = {
            "bucket_name": bucket_name,
            "object_key": object_key,
            "image_id": extract_image_id_from_s3_key(object_key),
        }

        log("INFO", "Processing image START", ctx)

        try:

            object_size = int(s3_record["s3"]["object"].get("size") or 0)
            validate_upload_size(object_size)

            image_data = download_image(bucket_name, object_key)

            log("INFO", "Image downloaded", {**ctx, "object_size": object_size})

            image_hash = generate_image_hash(image_data)

            log("INFO", "Image hash generated", {**ctx, "image_hash": image_hash})

            existing_item = find_existing_image(image_hash)

            if existing_item and existing_item["status"] != "failed":

                log(
                    "INFO",
                    "Duplicate image detected",
                    {**ctx, "existing_image_id": existing_item["image_id"]},
                )

                duplicate_records += 1

                continue

            image_type = validate_image(image_data)

            log("INFO", "Image validated", {**ctx, "image_type": image_type})

            moderation_labels = detect_moderation_labels(bucket_name, object_key)

            log(
                "INFO",
                "Rekognition completed",
                {**ctx, "labels_count": len(moderation_labels)},
            )

            extracted_text = extract_text_from_image(bucket_name, object_key)
            text_insights = None

            if extracted_text:
                log("INFO", "Textract completed", {**ctx, "text_length": len(extracted_text)})
                try:
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
                except Exception:
                    # Keep moderation flow resilient even if optional NLP analysis fails.
                    log("WARN", "Comprehend analysis failed; continuing without text insights", ctx)
            else:
                log("INFO", "Textract completed", {**ctx, "text_length": 0})

            store_moderation_result(
                moderation_labels,
                object_key,
                image_hash,
                extracted_text,
                text_insights,
            )

            log("INFO", "DynamoDB stored", ctx)

            send_success_notification(object_key, moderation_labels)

            log("INFO", "SNS sent", ctx)

            success_records += 1

            log("INFO", "Processing image END", ctx)

        except APPError as e:

            delete_invalid_upload(bucket_name, object_key)

            rejected_records += 1

            log(
                "WARN",
                f"Upload rejected and deleted: {e.message}",
                {
                    **ctx,
                    "code": e.code,
                },
            )

    log(
        "INFO",
        "Moderation batch END",
        {
            "total_records": total_records,
            "success_records": success_records,
            "duplicate_records": duplicate_records,
            "rejected_records": rejected_records,
        },
    )
