import unittest
from unittest.mock import patch

from common.exceptions import APPError
from _orchestrator_test_setup import orchestrator_handler, orchestrator_runtime_event


class OrchestratorHandlerTests(unittest.TestCase):
    # Verifies orchestrator handler captures events and delegates batch processing.
    def test_handler_calls_capture_and_processor(self) -> None:
        event = orchestrator_runtime_event()
        context = type("Ctx", (), {"aws_request_id": "req-1"})()

        with patch.object(orchestrator_handler, "capture_sample_event") as mock_capture:
            with patch.object(orchestrator_handler, "process_moderation_event") as mock_process:
                orchestrator_handler.lambda_handler(event, context)

        mock_capture.assert_called_once_with("content-moderation-orchestrator", event, context)
        mock_process.assert_called_once_with(event)

    # Verifies APPError exceptions from processing are re-raised for worker error handling.
    def test_handler_reraises_app_error_from_processor(self) -> None:
        event = orchestrator_runtime_event()
        context = type("Ctx", (), {"aws_request_id": "req-1"})()

        with patch.object(orchestrator_handler, "capture_sample_event"):
            with patch.object(
                orchestrator_handler,
                "process_moderation_event",
                side_effect=APPError("INVALID", "bad", 400),
            ):
                with self.assertRaises(APPError):
                    orchestrator_handler.lambda_handler(event, context)


if __name__ == "__main__":
    unittest.main()
