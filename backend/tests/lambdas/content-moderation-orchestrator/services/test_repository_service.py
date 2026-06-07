from unittest.mock import patch

from _orchestrator_test_setup import orchestrator_services

repository_service = orchestrator_services.repository_service


# Verifies stored moderation status toggles between safe and unsafe based on labels.
def test_store_moderation_result_status_safe_or_unsafe() -> None:
    with patch.object(repository_service.table, "put_item") as mock_put:
        repository_service.store_moderation_result([], "uploads/a.jpg", "hash-1")
        first_item = mock_put.call_args.kwargs["Item"]

        repository_service.store_moderation_result(
            [{"Name": "Violence", "Confidence": 99}],
            "uploads/b.jpg",
            "hash-2",
        )
        second_item = mock_put.call_args.kwargs["Item"]

        repository_service.store_moderation_result(
            [],
            "uploads/c.jpg",
            "hash-3",
            extracted_text="Detected text",
            text_insights={"sentiment": "NEGATIVE"},
        )
        third_item = mock_put.call_args.kwargs["Item"]

    assert first_item["status"] == "safe"
    assert not first_item["unsafe_detected"]
    assert second_item["status"] == "unsafe"
    assert second_item["unsafe_detected"]
    assert "extracted_text" not in first_item
    assert "extracted_text" in third_item
    assert third_item["extracted_text"] == "Detected text"
    assert third_item["text_insights"]["sentiment"] == "NEGATIVE"


# Verifies duplicate lookup returns None when no hash match exists.
def test_find_existing_image_returns_none_when_missing() -> None:
    with patch.object(repository_service.table, "query", return_value={"Items": []}) as mock_query:
        result = repository_service.find_existing_image("hash-1")

    assert result is None
    assert mock_query.call_args.kwargs["IndexName"] == "image_hash"
    assert mock_query.call_args.kwargs["Limit"] == 1


# Verifies duplicate lookup returns only the first match from the image-hash index query.
def test_find_existing_image_returns_first_item() -> None:
    expected = {"image_id": "img-1", "status": "safe"}
    with patch.object(
        repository_service.table,
        "query",
        return_value={"Items": [expected, {"image_id": "img-2"}]},
    ):
        result = repository_service.find_existing_image("hash-1")

    assert result == expected
