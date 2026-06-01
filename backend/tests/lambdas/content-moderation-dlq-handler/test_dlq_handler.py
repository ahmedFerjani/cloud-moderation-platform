import unittest
from unittest.mock import patch

from common.exceptions import APPError
from _dlq_test_setup import dlq_handler, dlq_runtime_event


class DlqHandlerTests(unittest.TestCase):
    # Verifies DLQ handler captures events and delegates message processing.
    def test_handler_calls_capture_and_processor(self) -> None:
        event = dlq_runtime_event()
        context = type("Ctx", (), {"aws_request_id": "req-1"})()

        with patch.object(dlq_handler, "capture_sample_event") as mock_capture:
            with patch.object(dlq_handler, "process_dlq_event") as mock_process:
                dlq_handler.lambda_handler(event, context)

        mock_capture.assert_called_once_with("content-moderation-dlq-handler", event, context)
        mock_process.assert_called_once_with(event)

    # Verifies APPError exceptions from DLQ processing are re-raised by the handler.
    def test_handler_reraises_app_error_from_processor(self) -> None:
        event = dlq_runtime_event()
        context = type("Ctx", (), {"aws_request_id": "req-1"})()

        with patch.object(dlq_handler, "capture_sample_event"):
            with patch.object(
                dlq_handler,
                "process_dlq_event",
                side_effect=APPError("INVALID", "bad", 400),
            ):
                with self.assertRaises(APPError):
                    dlq_handler.lambda_handler(event, context)


if __name__ == "__main__":
    unittest.main()
