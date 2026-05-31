import json
import unittest
from unittest.mock import patch

from _dlq_test_setup import dlq_processor, dlq_runtime_event


class DlqProcessorTests(unittest.TestCase):
    def test_extract_dlq_messages(self) -> None:
        event = dlq_runtime_event()
        messages = list(dlq_processor.extract_dlq_messages(event))

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["error"], "moved_to_dlq")

    def test_process_dlq_event_calls_store_and_notify(self) -> None:
        event = dlq_runtime_event()

        with patch.object(dlq_processor, "store_failure") as mock_store:
            with patch.object(dlq_processor, "send_notification") as mock_notify:
                dlq_processor.process_dlq_event(event)

        mock_store.assert_called_once()
        mock_notify.assert_called_once()

    def test_extract_dlq_messages_raises_on_invalid_json_body(self) -> None:
        event = {"Records": [{"body": "{bad-json"}]}

        with self.assertRaises(json.JSONDecodeError):
            list(dlq_processor.extract_dlq_messages(event))


if __name__ == "__main__":
    unittest.main()
