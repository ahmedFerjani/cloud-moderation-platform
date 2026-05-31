import unittest
from unittest.mock import patch

from _orchestrator_test_setup import orchestrator_processor, orchestrator_runtime_event


class OrchestratorProcessorTests(unittest.TestCase):
    def test_extract_s3_records_from_sqs_payload(self) -> None:
        event = orchestrator_runtime_event()
        records = list(orchestrator_processor.extract_s3_records(event))

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["eventSource"], "aws:s3")

    def test_duplicate_image_skips_processing(self) -> None:
        event = orchestrator_runtime_event()

        with patch.object(orchestrator_processor, "download_image", return_value=b"img"):
            with patch.object(orchestrator_processor, "generate_image_hash", return_value="hash-1"):
                with patch.object(
                    orchestrator_processor,
                    "find_existing_image",
                    return_value={"status": "safe", "image_id": "img-existing"},
                ):
                    with patch.object(orchestrator_processor, "validate_image") as mock_validate:
                        with patch.object(
                            orchestrator_processor, "detect_moderation_labels"
                        ) as mock_labels:
                            with patch.object(
                                orchestrator_processor, "store_moderation_result"
                            ) as mock_store:
                                with patch.object(
                                    orchestrator_processor, "send_success_notification"
                                ) as mock_notify:
                                    orchestrator_processor.process_moderation_event(event)

        mock_validate.assert_not_called()
        mock_labels.assert_not_called()
        mock_store.assert_not_called()
        mock_notify.assert_not_called()

    def test_app_error_path_deletes_invalid_upload(self) -> None:
        event = orchestrator_runtime_event()

        with patch.object(
            orchestrator_processor,
            "validate_upload_size",
            side_effect=orchestrator_processor.APPError("INVALID", "bad", 400),
        ):
            with patch.object(orchestrator_processor, "delete_invalid_upload") as mock_delete:
                orchestrator_processor.process_moderation_event(event)

        mock_delete.assert_called_once()

    def test_success_path_stores_and_notifies(self) -> None:
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
                                    "store_moderation_result",
                                ) as mock_store:
                                    with patch.object(
                                        orchestrator_processor,
                                        "send_success_notification",
                                    ) as mock_notify:
                                        with patch.object(
                                            orchestrator_processor,
                                            "delete_invalid_upload",
                                        ) as mock_delete:
                                            orchestrator_processor.process_moderation_event(event)

        mock_store.assert_called_once_with([], "uploads/sample-image.jpg", "hash-1")
        mock_notify.assert_called_once_with("uploads/sample-image.jpg", [])
        mock_delete.assert_not_called()

    def test_existing_failed_item_does_not_skip_processing(self) -> None:
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
                                    "store_moderation_result",
                                ) as mock_store:
                                    with patch.object(
                                        orchestrator_processor,
                                        "send_success_notification",
                                    ) as mock_notify:
                                        orchestrator_processor.process_moderation_event(event)

        mock_store.assert_called_once()
        mock_notify.assert_called_once()


if __name__ == "__main__":
    unittest.main()
