from decimal import Decimal

import boto3

from constants import MIN_CONFIDENCE

rekognition = boto3.client("rekognition")
textract = boto3.client("textract")


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
