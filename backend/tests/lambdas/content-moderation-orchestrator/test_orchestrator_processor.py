from unittest.mock import patch

from _orchestrator_test_setup import orchestrator_processor, orchestrator_runtime_event


# Verifies S3 records are extracted correctly from SQS wrapper payloads.
def test_extract_s3_records_from_sqs_payload() -> None:
    event = orchestrator_runtime_event()
    records = list(orchestrator_processor.extract_s3_records(event))

    assert len(records) == 1
    assert records[0]["eventSource"] == "aws:s3"


# Verifies duplicate detections short-circuit downstream moderation work.
def test_duplicate_image_skips_processing() -> None:
    event = orchestrator_runtime_event()

    with patch.object(orchestrator_processor, "download_image", return_value=b"img"):
        with patch.object(orchestrator_processor, "generate_image_hash", return_value="hash-1"):
            with patch.object(
                orchestrator_processor,
                "find_existing_image",
                return_value={"status": "safe", "image_id": "img-existing"},
            ):
                with patch.object(orchestrator_processor, "delete_uploaded_image") as mock_delete:
                    with patch.object(orchestrator_processor, "validate_image") as mock_validate:
                        with patch.object(
                            orchestrator_processor, "detect_moderation_labels"
                        ) as mock_labels:
                            with patch.object(
                                orchestrator_processor, "extract_text_from_image"
                            ) as mock_textract:
                                with patch.object(
                                    orchestrator_processor, "analyze_extracted_text"
                                ) as mock_comprehend:
                                    with patch.object(
                                        orchestrator_processor, "store_moderation_result"
                                    ) as mock_store:
                                        with patch.object(
                                            orchestrator_processor, "send_success_notification"
                                        ) as mock_notify:
                                            orchestrator_processor.process_moderation_event(event)

    mock_delete.assert_called_once_with("test-bucket", "uploads/sample-image.jpg")
    mock_validate.assert_not_called()
    mock_labels.assert_not_called()
    mock_textract.assert_not_called()
    mock_comprehend.assert_not_called()
    mock_store.assert_not_called()
    mock_notify.assert_not_called()


# Verifies business validation errors trigger cleanup by deleting the uploaded object.
def test_app_error_path_deletes_invalid_upload() -> None:
    event = orchestrator_runtime_event()

    with patch.object(
        orchestrator_processor,
        "validate_upload_size",
        side_effect=orchestrator_processor.APPError("INVALID", "bad", 400),
    ):
        with patch.object(orchestrator_processor, "delete_uploaded_image") as mock_delete:
            orchestrator_processor.process_moderation_event(event)

    mock_delete.assert_called_once()


# Verifies successful moderation stores results, emits notifications, and avoids deletion.
def test_success_path_stores_and_notifies() -> None:
    event = orchestrator_runtime_event()

    with patch.object(orchestrator_processor, "validate_upload_size"):
        with patch.object(orchestrator_processor, "download_image", return_value=b"img"):
            with patch.object(
                orchestrator_processor,
                "generate_image_hash",
                return_value="hash-1",
            ):
                with patch.object(
                    orchestrator_processor,
                    "find_existing_image",
                    return_value=None,
                ):
                    with patch.object(
                        orchestrator_processor,
                        "validate_image",
                        return_value="jpeg",
                    ):
                        with patch.object(
                            orchestrator_processor,
                            "detect_moderation_labels",
                            return_value=[],
                        ):
                            with patch.object(
                                orchestrator_processor,
                                "extract_text_from_image",
                                return_value="Sample extracted text",
                            ):
                                with patch.object(
                                    orchestrator_processor,
                                    "analyze_extracted_text",
                                    return_value={"sentiment": "NEGATIVE"},
                                ):
                                    with patch.object(
                                        orchestrator_processor,
                                        "store_moderation_result",
                                    ) as mock_store:
                                        with patch.object(
                                            orchestrator_processor,
                                            "send_success_notification",
                                        ) as mock_notify:
                                            with patch.object(
                                                orchestrator_processor,
                                                "delete_uploaded_image",
                                            ) as mock_delete:
                                                orchestrator_processor.process_moderation_event(
                                                    event
                                                )

    mock_store.assert_called_once_with(
        [],
        "uploads/sample-image.jpg",
        "hash-1",
        "Sample extracted text",
        {"sentiment": "NEGATIVE"},
    )
    mock_notify.assert_called_once_with("uploads/sample-image.jpg", [])
    mock_delete.assert_not_called()


# Verifies previously failed duplicates are retried instead of being skipped.
def test_existing_failed_item_does_not_skip_processing() -> None:
    event = orchestrator_runtime_event()

    with patch.object(orchestrator_processor, "validate_upload_size"):
        with patch.object(orchestrator_processor, "download_image", return_value=b"img"):
            with patch.object(
                orchestrator_processor,
                "generate_image_hash",
                return_value="hash-1",
            ):
                with patch.object(
                    orchestrator_processor,
                    "find_existing_image",
                    return_value={
                        "status": "failed",
                        "image_id": "img-existing",
                    },
                ):
                    with patch.object(
                        orchestrator_processor,
                        "validate_image",
                        return_value="jpeg",
                    ):
                        with patch.object(
                            orchestrator_processor,
                            "detect_moderation_labels",
                            return_value=[],
                        ):
                            with patch.object(
                                orchestrator_processor,
                                "extract_text_from_image",
                                return_value=None,
                            ):
                                with patch.object(
                                    orchestrator_processor,
                                    "analyze_extracted_text",
                                ) as mock_comprehend:
                                    with patch.object(
                                        orchestrator_processor,
                                        "store_moderation_result",
                                    ) as mock_store:
                                        with patch.object(
                                            orchestrator_processor,
                                            "send_success_notification",
                                        ) as mock_notify:
                                            orchestrator_processor.process_moderation_event(event)

    mock_comprehend.assert_not_called()
    mock_store.assert_called_once()
    mock_notify.assert_called_once()
