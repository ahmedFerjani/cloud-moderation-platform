import json
import unittest
from unittest.mock import patch

from _api_test_setup import api_router, api_runtime_event


class ApiRouterTests(unittest.TestCase):
    def test_post_generate_upload_route_uses_body(self) -> None:
        event = api_runtime_event("api-generate-upload-url.json")

        with patch.object(api_router, "generate_upload_url", return_value={"ok": True}) as mock_fn:
            result = api_router.route_request(event)

        self.assertEqual(result, {"ok": True})
        mock_fn.assert_called_once_with({"content_type": "image/jpeg"})

    def test_get_results_route_calls_service_with_parsed_limit(self) -> None:
        event = api_runtime_event("api-moderation-results.json")
        event["queryStringParameters"] = {"limit": "5"}

        with patch.object(
            api_router, "get_moderation_results", return_value={"ok": True}
        ) as mock_results:
            result = api_router.route_request(event)

        self.assertEqual(result, {"ok": True})
        mock_results.assert_called_once_with(5)

    def test_get_by_id_route_calls_service(self) -> None:
        event = api_runtime_event("api-moderation-result-by-image-id.json")

        with patch.object(
            api_router, "get_moderation_result", return_value={"ok": True}
        ) as mock_result:
            result = api_router.route_request(event)

        self.assertEqual(result, {"ok": True})
        mock_result.assert_called_once_with("00000000-0000-0000-0000-000000000000")

    def test_missing_body_raises(self) -> None:
        event = api_runtime_event("api-generate-upload-url.json")
        event.pop("body", None)

        with self.assertRaises(api_router.APPError) as ctx:
            api_router.route_request(event)

        self.assertEqual(ctx.exception.code, "MISSING_REQUEST_BODY")

    def test_invalid_json_body_raises_decode_error(self) -> None:
        event = api_runtime_event("api-generate-upload-url.json")
        event["body"] = "{bad-json"

        with self.assertRaises(json.JSONDecodeError):
            api_router.route_request(event)

    def test_unknown_route_raises_not_found(self) -> None:
        event = api_runtime_event("api-moderation-results.json")
        event["requestContext"]["http"]["method"] = "DELETE"
        event["rawPath"] = "/not-a-real-route"

        with self.assertRaises(api_router.APPError) as ctx:
            api_router.route_request(event)

        self.assertEqual(ctx.exception.code, "ROUTE_NOT_FOUND")
        self.assertEqual(ctx.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
