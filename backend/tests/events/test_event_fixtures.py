import json
import re
from pathlib import Path
from typing import Any

EVENTS_DIR = Path(__file__).resolve().parents[2] / "events"

# Match standalone 12-digit account IDs, but ignore UUID segments like
# 00000000-0000-0000-0000-000000000000.
ACCOUNT_ID_RE = re.compile(r"(?<![-\d])\d{12}(?![-\d])")
IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


def _iter_strings(value: Any):
    if isinstance(value, dict):
        for item in value.values():
            yield from _iter_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_strings(item)
    elif isinstance(value, str):
        yield value


def _load_fixture(name: str) -> dict[str, Any]:
    return json.loads((EVENTS_DIR / name).read_text(encoding="utf-8"))


# Verifies all fixture files are scrubbed of raw account IDs, IPs, and legacy resource names.
def test_all_fixtures_have_no_raw_account_ids_or_ips() -> None:
    for path in sorted(EVENTS_DIR.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        all_strings = list(_iter_strings(payload))

        joined = "\n".join(all_strings)
        assert ACCOUNT_ID_RE.search(joined) is None, f"Raw account ID found in {path.name}"
        assert IPV4_RE.search(joined) is None, f"Raw IP address found in {path.name}"
        assert "image-labeling-queue" not in joined
        assert "image-labeling-dlq" not in joined
        assert "image-labels-" not in joined


# Verifies API upload fixture includes expected redactions in request metadata.
def test_api_generate_upload_fixture_redactions() -> None:
    payload = _load_fixture("api-generate-upload-url.json")

    assert payload["headers"]["host"] == "<redacted>"
    assert payload["headers"]["user-agent"] == "<redacted>"
    assert payload["headers"]["x-forwarded-for"] == "<redacted>"
    assert payload["requestContext"]["http"]["sourceIp"] == "<redacted>"
    assert payload["requestContext"]["http"]["userAgent"] == "<redacted>"


# Verifies image ID fixture values are normalized consistently across route and context fields.
def test_api_moderation_by_image_id_fixture_is_normalized() -> None:
    payload = _load_fixture("api-moderation-result-by-image-id.json")
    expected_id = "00000000-0000-0000-0000-000000000000"

    assert payload["pathParameters"]["imageId"] == expected_id
    assert expected_id in payload["rawPath"]
    assert expected_id in payload["requestContext"]["http"]["path"]


# Checks orchestrator fixture normalization.
def test_orchestrator_fixture_resource_names_normalized() -> None:
    payload = _load_fixture("orchestrator-sqs-event.json")
    record = payload["Records"][0]
    s3_object = record["body"]["Records"][0]["s3"]["object"]

    assert record["body"]["Records"][0]["s3"]["configurationId"] == "<normalized>"
    assert record["body"]["Records"][0]["s3"]["bucket"]["name"] == "<normalized-bucket>"
    assert record["body"]["Records"][0]["s3"]["bucket"]["arn"] == "arn:aws:s3:::<normalized-bucket>"
    assert s3_object["key"] == "uploads/sample-image.jpg"
    assert s3_object["eTag"] == "<normalized>"
    assert s3_object["versionId"] == "<normalized>"
    assert s3_object["sequencer"] == "<normalized>"
    assert record["md5OfBody"] == "<normalized>"
    assert record["eventSourceARN"] == "arn:aws:sqs:us-east-1:<redacted>:<normalized-resource>"


# Verifies DLQ fixture uses normalized queue resource identifiers.
def test_dlq_fixture_resource_names_normalized() -> None:
    payload = _load_fixture("dlq-sqs-event.json")
    record = payload["Records"][0]

    assert (
        record["attributes"]["DeadLetterQueueSourceArn"]
        == "arn:aws:sqs:us-east-1:<redacted>:<normalized-resource>"
    )
    assert record["eventSourceARN"] == "arn:aws:sqs:us-east-1:<redacted>:<normalized-resource>"


# Verifies upload fixture aligns with API router POST contract expectations.
def test_api_post_fixture_matches_router_contract() -> None:
    payload = _load_fixture("api-generate-upload-url.json")

    assert payload["requestContext"]["http"]["method"] == "POST"
    assert payload["rawPath"] == "/generate-upload-url"
    assert "body" in payload
    assert payload["body"]["content_type"] == "image/jpeg"


# Verifies list fixture aligns with API router GET collection contract.
def test_api_list_fixture_matches_router_contract() -> None:
    payload = _load_fixture("api-moderation-results.json")

    assert payload["requestContext"]["http"]["method"] == "GET"
    assert payload["rawPath"] == "/moderation-results"
    assert "pathParameters" not in payload


# Verifies by-ID fixture aligns with API router path-parameter contract.
def test_api_by_id_fixture_matches_router_contract() -> None:
    payload = _load_fixture("api-moderation-result-by-image-id.json")

    assert payload["requestContext"]["http"]["method"] == "GET"
    assert payload["routeKey"] == "GET /moderation-results/{imageId}"
    assert "pathParameters" in payload
    assert "imageId" in payload["pathParameters"]


# Verifies orchestrator fixture matches the processor's expected nested SQS-to-S3 structure.
def test_orchestrator_fixture_matches_processor_contract() -> None:
    payload = _load_fixture("orchestrator-sqs-event.json")
    outer_record = payload["Records"][0]
    inner_record = outer_record["body"]["Records"][0]

    assert "body" in outer_record
    assert "Records" in outer_record["body"]
    assert inner_record["eventSource"] == "aws:s3"
    assert "s3" in inner_record
    assert "bucket" in inner_record["s3"]
    assert "object" in inner_record["s3"]


# Verifies DLQ fixture matches the processor contract for body and SQS attributes.
def test_dlq_fixture_matches_processor_contract() -> None:
    payload = _load_fixture("dlq-sqs-event.json")
    outer_record = payload["Records"][0]
    inner_record = outer_record["body"]["Records"][0]

    assert "body" in outer_record
    assert "Records" in outer_record["body"]
    assert inner_record["eventSource"] == "aws:s3"
    assert "attributes" in outer_record
    assert "ApproximateReceiveCount" in outer_record["attributes"]
