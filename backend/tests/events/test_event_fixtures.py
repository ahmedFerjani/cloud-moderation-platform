import json
import re
import unittest
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


class EventFixturesSafetyTests(unittest.TestCase):
    # Verifies all fixture files are scrubbed of raw account IDs, IPs, and legacy resource names.
    def test_all_fixtures_have_no_raw_account_ids_or_ips(self) -> None:
        for path in sorted(EVENTS_DIR.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            all_strings = list(_iter_strings(payload))

            joined = "\n".join(all_strings)
            self.assertIsNone(ACCOUNT_ID_RE.search(joined), f"Raw account ID found in {path.name}")
            self.assertIsNone(IPV4_RE.search(joined), f"Raw IP address found in {path.name}")
            self.assertNotIn("image-labeling-queue", joined)
            self.assertNotIn("image-labeling-dlq", joined)
            self.assertNotIn("image-labels-", joined)

    # Verifies API upload fixture includes expected redactions in request metadata.
    def test_api_generate_upload_fixture_redactions(self) -> None:
        payload = _load_fixture("api-generate-upload-url.json")

        self.assertEqual(payload["headers"]["host"], "<redacted>")
        self.assertEqual(payload["headers"]["user-agent"], "<redacted>")
        self.assertEqual(payload["headers"]["x-forwarded-for"], "<redacted>")
        self.assertEqual(payload["requestContext"]["http"]["sourceIp"], "<redacted>")
        self.assertEqual(payload["requestContext"]["http"]["userAgent"], "<redacted>")

    # Verifies image ID fixture values are normalized consistently across route and context fields.
    def test_api_moderation_by_image_id_fixture_is_normalized(self) -> None:
        payload = _load_fixture("api-moderation-result-by-image-id.json")
        expected_id = "00000000-0000-0000-0000-000000000000"

        self.assertEqual(
            payload["pathParameters"]["imageId"],
            expected_id,
        )
        self.assertIn(expected_id, payload["rawPath"])
        self.assertIn(expected_id, payload["requestContext"]["http"]["path"])

    # Checks orchestrator fixture normalizeation.
    def test_orchestrator_fixture_resource_names_normalized(self) -> None:
        payload = _load_fixture("orchestrator-sqs-event.json")
        record = payload["Records"][0]
        s3_object = record["body"]["Records"][0]["s3"]["object"]

        self.assertEqual(
            record["body"]["Records"][0]["s3"]["configurationId"],
            "<normalized>",
        )
        self.assertEqual(
            record["body"]["Records"][0]["s3"]["bucket"]["name"],
            "<normalized-bucket>",
        )
        self.assertEqual(
            record["body"]["Records"][0]["s3"]["bucket"]["arn"],
            "arn:aws:s3:::<normalized-bucket>",
        )
        self.assertEqual(s3_object["key"], "uploads/sample-image.jpg")
        self.assertEqual(s3_object["eTag"], "<normalized>")
        self.assertEqual(s3_object["versionId"], "<normalized>")
        self.assertEqual(s3_object["sequencer"], "<normalized>")
        self.assertEqual(record["md5OfBody"], "<normalized>")
        self.assertEqual(
            record["eventSourceARN"],
            "arn:aws:sqs:us-east-1:<redacted>:<normalized-resource>",
        )

    # Verifies DLQ fixture uses normalized queue resource identifiers.
    def test_dlq_fixture_resource_names_normalized(self) -> None:
        payload = _load_fixture("dlq-sqs-event.json")
        record = payload["Records"][0]

        self.assertEqual(
            record["attributes"]["DeadLetterQueueSourceArn"],
            "arn:aws:sqs:us-east-1:<redacted>:<normalized-resource>",
        )
        self.assertEqual(
            record["eventSourceARN"],
            "arn:aws:sqs:us-east-1:<redacted>:<normalized-resource>",
        )

    # Verifies upload fixture aligns with API router POST contract expectations.
    def test_api_post_fixture_matches_router_contract(self) -> None:
        payload = _load_fixture("api-generate-upload-url.json")

        self.assertEqual(payload["requestContext"]["http"]["method"], "POST")
        self.assertEqual(payload["rawPath"], "/generate-upload-url")
        self.assertIn("body", payload)
        self.assertEqual(payload["body"]["content_type"], "image/jpeg")

    # Verifies list fixture aligns with API router GET collection contract.
    def test_api_list_fixture_matches_router_contract(self) -> None:
        payload = _load_fixture("api-moderation-results.json")

        self.assertEqual(payload["requestContext"]["http"]["method"], "GET")
        self.assertEqual(payload["rawPath"], "/moderation-results")
        self.assertNotIn("pathParameters", payload)

    # Verifies by-ID fixture aligns with API router path-parameter contract.
    def test_api_by_id_fixture_matches_router_contract(self) -> None:
        payload = _load_fixture("api-moderation-result-by-image-id.json")

        self.assertEqual(payload["requestContext"]["http"]["method"], "GET")
        self.assertEqual(payload["routeKey"], "GET /moderation-results/{imageId}")
        self.assertIn("pathParameters", payload)
        self.assertIn("imageId", payload["pathParameters"])

    # Verifies orchestrator fixture matches the processor's expected nested SQS-to-S3 structure.
    def test_orchestrator_fixture_matches_processor_contract(self) -> None:
        payload = _load_fixture("orchestrator-sqs-event.json")
        outer_record = payload["Records"][0]
        inner_record = outer_record["body"]["Records"][0]

        self.assertIn("body", outer_record)
        self.assertIn("Records", outer_record["body"])
        self.assertEqual(inner_record["eventSource"], "aws:s3")
        self.assertIn("s3", inner_record)
        self.assertIn("bucket", inner_record["s3"])
        self.assertIn("object", inner_record["s3"])

    # Verifies DLQ fixture matches the processor contract for body and SQS attributes.
    def test_dlq_fixture_matches_processor_contract(self) -> None:
        payload = _load_fixture("dlq-sqs-event.json")
        outer_record = payload["Records"][0]
        inner_record = outer_record["body"]["Records"][0]

        self.assertIn("body", outer_record)
        self.assertIn("Records", outer_record["body"])
        self.assertEqual(inner_record["eventSource"], "aws:s3")
        self.assertIn("attributes", outer_record)
        self.assertIn("ApproximateReceiveCount", outer_record["attributes"])


if __name__ == "__main__":
    unittest.main()
