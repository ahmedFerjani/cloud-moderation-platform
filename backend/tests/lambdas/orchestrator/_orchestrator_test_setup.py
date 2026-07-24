import json
import os
import sys
from pathlib import Path

from helpers import ensure_sys_path, find_backend_root, load_event, load_module

BACKEND_ROOT = find_backend_root(Path(__file__))
COMMON_PATH = BACKEND_ROOT / "layers" / "serverless_utils" / "python"
ORCHESTRATOR_PATH = BACKEND_ROOT / "lambdas" / "orchestrator"
EVENTS_PATH = BACKEND_ROOT / "events"

ensure_sys_path((COMMON_PATH, ORCHESTRATOR_PATH))

os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("TABLE_NAME", "test-table")
os.environ.setdefault("CONNECTIONS_TABLE_NAME", "test-connections-table")
os.environ.setdefault(
    "WEBSOCKET_ENDPOINT_URL", "https://test-endpoint.execute-api.us-east-1.amazonaws.com/test"
)


def orchestrator_runtime_event() -> dict:
    event = load_event(EVENTS_PATH, "orchestrator-sqs-event.json")
    for record in event["Records"]:
        # Lambda receives SQS body as a string; stored fixture keeps parsed JSON.
        if isinstance(record.get("body"), dict):
            record["body"] = json.dumps(record["body"])
    return event


orchestrator_validation = load_module(
    "orchestrator_validation",
    ORCHESTRATOR_PATH / "validation.py",
    # Prevent cross-test collision with other lambda constants modules.
    clear_modules=("constants", "validation"),
)
sys.modules["validation"] = orchestrator_validation
orchestrator_services = load_module(
    "services",
    ORCHESTRATOR_PATH / "services" / "__init__.py",
    # Prevent cross-test collision with other lambda constants modules.
    clear_modules=("constants", "services"),
)
orchestrator_services = sys.modules["services"]
sys.modules["services"] = orchestrator_services
orchestrator_processor = load_module("orchestrator_processor", ORCHESTRATOR_PATH / "processor.py")
sys.modules["processor"] = orchestrator_processor
orchestrator_handler = load_module("orchestrator_handler", ORCHESTRATOR_PATH / "handler.py")
