import json
import unittest
from unittest.mock import MagicMock, patch

from _api_test_setup import api_services


class ApiServicesTests(unittest.TestCase):
    # Verifies limit parsing applies default and max-cap behaviors.
    def test_parse_limit_default_and_cap(self) -> None:
        self.assertEqual(api_services.parse_limit({}), 20)
        self.assertEqual(api_services.parse_limit({"limit": "7"}), 7)
        self.assertEqual(api_services.parse_limit({"limit": "999"}), 100)

    # Verifies non-numeric limit values are rejected with validation errors.
    def test_parse_limit_invalid_raises(self) -> None:
        with self.assertRaises(api_services.APPError) as ctx:
            api_services.parse_limit({"limit": "abc"})

        self.assertEqual(ctx.exception.code, "INVALID_LIMIT")
        self.assertEqual(ctx.exception.status_code, 400)

    # Verifies zero is rejected as an invalid pagination limit.
    def test_parse_limit_zero_raises(self) -> None:
        with self.assertRaises(api_services.APPError) as ctx:
            api_services.parse_limit({"limit": "0"})

        self.assertEqual(ctx.exception.code, "INVALID_LIMIT")
        self.assertEqual(ctx.exception.status_code, 400)

    # Verifies negative limits are rejected as invalid input.
    def test_parse_limit_negative_raises(self) -> None:
        with self.assertRaises(api_services.APPError) as ctx:
            api_services.parse_limit({"limit": "-1"})

        self.assertEqual(ctx.exception.code, "INVALID_LIMIT")
        self.assertEqual(ctx.exception.status_code, 400)

    # Verifies upload URL generation returns stable response shape and object naming conventions.
    @patch.object(api_services, "log")
    def test_generate_upload_url_success(self, _mock_log: MagicMock) -> None:
        with patch.object(api_services.uuid, "uuid4", return_value="id-123"):
            with patch.object(api_services.s3, "generate_presigned_post") as mock_post:
                mock_post.return_value = {
                    "url": "https://example.com/upload",
                    "fields": {"Content-Type": "image/jpeg"},
                }
                response = api_services.generate_upload_url({"content_type": "image/jpeg"})

        body = json.loads(response["body"])
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["image_id"], "id-123")
        self.assertEqual(body["object_key"], "uploads/id-123.jpg")
        mock_post.assert_called_once()

    # Verifies unsupported MIME types are rejected before presigned URL generation.
    def test_generate_upload_url_rejects_invalid_content_type(self) -> None:
        with self.assertRaises(api_services.APPError) as ctx:
            api_services.generate_upload_url({"content_type": "application/pdf"})

        self.assertEqual(ctx.exception.code, "UNSUPPORTED_CONTENT_TYPE")

    # Verifies missing content type is rejected as required input.
    def test_generate_upload_url_requires_content_type(self) -> None:
        with self.assertRaises(api_services.APPError) as ctx:
            api_services.generate_upload_url({})

        self.assertEqual(ctx.exception.code, "MISSING_CONTENT_TYPE")

    # Verifies detail lookup raises not-found when DynamoDB has no matching moderation item.
    def test_get_moderation_result_not_found(self) -> None:
        with patch.object(api_services.table, "get_item", return_value={}):
            with self.assertRaises(api_services.APPError) as ctx:
                api_services.get_moderation_result("img-1")

        self.assertEqual(ctx.exception.code, "MODERATION_RESULT_NOT_FOUND")

    # Verifies detail lookup returns a successful API response for existing moderation items.
    def test_get_moderation_result_success(self) -> None:
        item = {"image_id": "img-1", "status": "safe"}
        with patch.object(api_services.table, "get_item", return_value={"Item": item}):
            response = api_services.get_moderation_result("img-1")

        body = json.loads(response["body"])
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body, item)

    # Verifies list lookup returns items, count, and pagination key from DynamoDB scan results.
    def test_get_moderation_results_success(self) -> None:
        with patch.object(
            api_services.table,
            "scan",
            return_value={
                "Items": [{"image_id": "img-1"}],
                "Count": 1,
                "LastEvaluatedKey": {"image_id": "img-1"},
            },
        ) as mock_scan:
            response = api_services.get_moderation_results(5)

        body = json.loads(response["body"])
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["count"], 1)
        self.assertEqual(body["items"][0]["image_id"], "img-1")
        self.assertEqual(body["last_evaluated_key"], {"image_id": "img-1"})
        mock_scan.assert_called_once_with(Limit=5)


if __name__ == "__main__":
    unittest.main()
