import json
import os
import sys
from pathlib import Path

from helpers import ensure_sys_path, find_backend_root, load_event, load_module

BACKEND_ROOT = find_backend_root(Path(__file__))
COMMON_PATH = BACKEND_ROOT / "layers" / "serverless_utils" / "python"
DLQ_PATH = BACKEND_ROOT / "lambdas" / "dlq_handler"
EVENTS_PATH = BACKEND_ROOT / "events"

ensure_sys_path((COMMON_PATH, DLQ_PATH))

os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("TABLE_NAME", "test-table")


def dlq_runtime_event() -> dict:
    event = load_event(EVENTS_PATH, "dlq-sqs-event.json")
    for record in event["Records"]:
        if isinstance(record.get("body"), dict):
            # DLQ handler expects a compact failure message in each SQS body string.
            message = {
                "s3_key": record["body"]["Records"][0]["s3"]["object"]["key"],
                "error": "moved_to_dlq",
            }
            record["body"] = json.dumps(message)
    return event


dlq_services = load_module(
    "dlq_services",
    DLQ_PATH / "services.py",
    clear_modules=("constants",),
)
sys.modules["services"] = dlq_services
dlq_processor = load_module("dlq_processor", DLQ_PATH / "processor.py")
sys.modules["processor"] = dlq_processor
dlq_handler = load_module("dlq_handler", DLQ_PATH / "handler.py")
