import json
from unittest.mock import patch

import pytest

from _api_test_setup import api_router


# Verifies POST upload route parses body JSON and forwards payload to upload generation service.
def test_post_generate_upload_route_uses_body(api_event_factory) -> None:
    event = api_event_factory("api-generate-upload-url.json")

    with patch.object(api_router, "generate_upload_url", return_value={"ok": True}) as mock_fn:
        result = api_router.route_request(event)

    assert result == {"ok": True}
    mock_fn.assert_called_once_with({"content_type": "image/jpeg"})


# Verifies list route parses limit and forwards the normalized value to service layer.
def test_get_results_route_calls_service_with_parsed_limit(api_event_factory) -> None:
    event = api_event_factory("api-moderation-results.json")
    event["queryStringParameters"] = {"limit": "5"}

    with patch.object(
        api_router, "get_moderation_results", return_value={"ok": True}
    ) as mock_results:
        result = api_router.route_request(event)

    assert result == {"ok": True}
    mock_results.assert_called_once_with(5, None)


# Verifies list route forwards optional pagination cursor when provided.
def test_get_results_route_calls_service_with_last_evaluated_key(api_event_factory) -> None:
    event = api_event_factory("api-moderation-results.json")
    event["queryStringParameters"] = {
        "limit": "5",
        "last_evaluated_key": json.dumps({"image_id": "img-1"}),
    }

    with patch.object(
        api_router, "get_moderation_results", return_value={"ok": True}
    ) as mock_results:
        result = api_router.route_request(event)

    assert result == {"ok": True}
    mock_results.assert_called_once_with(5, {"image_id": "img-1"})


# Verifies by-ID route extracts image identifier and delegates to detail service.
def test_get_by_id_route_calls_service(api_event_factory) -> None:
    event = api_event_factory("api-moderation-result-by-image-id.json")

    with patch.object(
        api_router, "get_moderation_result", return_value={"ok": True}
    ) as mock_result:
        result = api_router.route_request(event)

    assert result == {"ok": True}
    mock_result.assert_called_once_with("00000000-0000-0000-0000-000000000000")


# Verifies upload route rejects requests with missing bodies.
def test_missing_body_raises(api_event_factory) -> None:
    event = api_event_factory("api-generate-upload-url.json")
    event.pop("body", None)

    with pytest.raises(api_router.APPError) as ctx:
        api_router.route_request(event)

    assert ctx.value.code == "MISSING_REQUEST_BODY"


# Verifies malformed JSON bodies surface as decode errors for middleware translation.
def test_invalid_json_body_raises_decode_error(api_event_factory) -> None:
    event = api_event_factory("api-generate-upload-url.json")
    event["body"] = "{bad-json"

    with pytest.raises(json.JSONDecodeError):
        api_router.route_request(event)


# Verifies unknown method/path combinations are rejected with route-not-found errors.
@pytest.mark.parametrize(
    "method,path",
    [("DELETE", "/not-a-real-route"), ("PATCH", "/unknown")],
)
def test_unknown_route_raises_not_found(api_event_factory, method: str, path: str) -> None:
    event = api_event_factory("api-moderation-results.json")
    event["requestContext"]["http"]["method"] = method
    event["rawPath"] = path

    with pytest.raises(api_router.APPError) as ctx:
        api_router.route_request(event)

    assert ctx.value.code == "ROUTE_NOT_FOUND"
    assert ctx.value.status_code == 404
