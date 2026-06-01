import os
import sys
import unittest
import importlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

COMMON_LAYER_PATH = (
    Path(__file__).resolve().parents[2] / "layers" / "serverless-utils-layer" / "python"
)

if str(COMMON_LAYER_PATH) not in sys.path:
    sys.path.insert(0, str(COMMON_LAYER_PATH))

event_capture = importlib.import_module("common.event_capture")


class EventCaptureSanitizationTests(unittest.TestCase):
    # Verifies API Gateway event fields and JSON body values are sanitized before capture.
    def test_sanitize_api_gateway_fields_and_json_body(self) -> None:
        raw_event = {
            "headers": {
                "host": "abc123.execute-api.us-east-1.amazonaws.com",
                "user-agent": "PostmanRuntime/7.53.0",
                "x-forwarded-for": "196.178.216.60",
            },
            "requestContext": {
                "apiId": "abc123",
                "domainName": "abc123.execute-api.us-east-1.amazonaws.com",
                "http": {
                    "sourceIp": "196.178.216.60",
                    "userAgent": "PostmanRuntime/7.53.0",
                    "method": "POST",
                },
                "time": "31/May/2026:10:00:00 +0000",
                "requestId": "req-1",
            },
            "body": '{"content_type":"image/jpeg","account":"123456789012"}',
            "isBase64Encoded": False,
        }

        sanitized = event_capture._sanitize(raw_event)

        self.assertEqual(sanitized["headers"]["host"], event_capture.REDACTED_VALUE)
        self.assertEqual(sanitized["headers"]["user-agent"], event_capture.REDACTED_VALUE)
        self.assertEqual(sanitized["headers"]["x-forwarded-for"], event_capture.REDACTED_VALUE)
        self.assertEqual(
            sanitized["requestContext"]["http"]["sourceIp"],
            event_capture.REDACTED_VALUE,
        )
        self.assertEqual(
            sanitized["requestContext"]["http"]["userAgent"],
            event_capture.REDACTED_VALUE,
        )
        self.assertEqual(sanitized["requestContext"]["requestId"], event_capture.REDACTED_VALUE)
        self.assertEqual(sanitized["requestContext"]["time"], event_capture.REDACTED_VALUE)
        self.assertEqual(sanitized["requestContext"]["http"]["method"], "POST")

        # Body JSON should be parsed and string account IDs should be masked.
        self.assertIsInstance(sanitized["body"], dict)
        self.assertEqual(sanitized["body"]["content_type"], "image/jpeg")
        self.assertEqual(sanitized["body"]["account"], event_capture.REDACTED_VALUE)

    # Verifies nested SQS payloads have sensitive handles, source IPs, and ARNs redacted.
    def test_sanitize_sqs_nested_source_ip_and_arns(self) -> None:
        raw_event = {
            "Records": [
                {
                    "receiptHandle": "AQEB123",
                    "body": {
                        "Records": [{"requestParameters": {"sourceIPAddress": "196.178.216.60"}}]
                    },
                    "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:image-queue",
                }
            ]
        }

        sanitized = event_capture._sanitize(raw_event)
        record = sanitized["Records"][0]

        self.assertEqual(record["receiptHandle"], event_capture.REDACTED_VALUE)
        self.assertEqual(
            record["body"]["Records"][0]["requestParameters"]["sourceIPAddress"],
            event_capture.REDACTED_VALUE,
        )
        self.assertEqual(
            record["eventSourceARN"],
            "arn:aws:sqs:us-east-1:<redacted>:image-queue",
        )

    # Verifies AWS mode captures the sanitized payload via structured logging.
    def test_capture_logs_json_payload_in_aws_mode(self) -> None:
        event = {"hello": "world"}
        context = SimpleNamespace(aws_request_id="req-123")

        with patch.dict(
            os.environ,
            {"CAPTURE_SAMPLE_EVENTS": "true", "AWS_SAM_LOCAL": "false"},
            clear=False,
        ):
            with patch("common.event_capture.log") as mock_log:
                event_capture.capture_sample_event("content-moderation-api", event, context)

        mock_log.assert_called_once()
        _, _, extra = mock_log.call_args.args
        self.assertEqual(extra["lambda_name"], "content-moderation-api")
        self.assertEqual(extra["aws_request_id"], "req-123")
        self.assertEqual(extra["event_payload"], event)
        self.assertEqual(extra["event_truncated"], 0)

    # Verifies SAM local mode writes captured events to fixture files instead of logging payloads.
    def test_capture_saves_event_to_file_in_sam_local_mode(self) -> None:
        event = {"hello": "world"}
        context = SimpleNamespace(aws_request_id="req-local")

        with patch.dict(
            os.environ,
            {"CAPTURE_SAMPLE_EVENTS": "true", "AWS_SAM_LOCAL": "true"},
            clear=False,
        ):
            with patch(
                "common.event_capture._save_event_to_file",
                return_value="events/captured/sample.json",
            ) as mock_save:
                with patch("common.event_capture.log") as mock_log:
                    event_capture.capture_sample_event("content-moderation-api", event, context)

        mock_save.assert_called_once_with("content-moderation-api", event, "req-local")
        mock_log.assert_called_once()
        _, _, extra = mock_log.call_args.args
        self.assertEqual(extra["lambda_name"], "content-moderation-api")
        self.assertEqual(extra["aws_request_id"], "req-local")
        self.assertEqual(extra["event_file_path"], "events/captured/sample.json")

    # Verifies oversized events are truncated to prevent noisy or oversized telemetry payloads.
    def test_capture_truncates_oversized_payload_in_aws_mode(self) -> None:
        event = {"items": ["x" * 100] * 300}
        context = SimpleNamespace(aws_request_id="req-large")

        with patch.dict(
            os.environ,
            {"CAPTURE_SAMPLE_EVENTS": "true", "AWS_SAM_LOCAL": "false"},
            clear=False,
        ):
            with patch("common.event_capture.log") as mock_log:
                event_capture.capture_sample_event("content-moderation-api", event, context)

        _, _, extra = mock_log.call_args.args
        self.assertEqual(extra["event_truncated"], 1)
        self.assertIsInstance(extra["event_payload"], str)
        self.assertTrue(
            extra["event_payload"].endswith(event_capture.TRUNCATED_VALUE),
        )


if __name__ == "__main__":
    unittest.main()
