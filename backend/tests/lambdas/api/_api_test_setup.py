import json
import os
import sys
from pathlib import Path

from helpers import ensure_sys_path, find_backend_root, load_event, load_module

BACKEND_ROOT = find_backend_root(Path(__file__))
COMMON_PATH = BACKEND_ROOT / "layers" / "serverless_utils" / "python"
API_PATH = BACKEND_ROOT / "lambdas" / "api"
EVENTS_PATH = BACKEND_ROOT / "events"

ensure_sys_path((COMMON_PATH, API_PATH))

os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("BUCKET_NAME", "test-bucket")
os.environ.setdefault("TABLE_NAME", "test-table")


def api_runtime_event(name: str) -> dict:
    event = load_event(EVENTS_PATH, name)
    # Saved fixtures keep body as dict for readability; API Gateway delivers it as JSON string.
    if isinstance(event.get("body"), dict):
        event["body"] = json.dumps(event["body"])
    return event


api_validation = load_module("api_validation", API_PATH / "validation.py")
sys.modules["validation"] = api_validation
api_services = load_module(
    "api_services",
    API_PATH / "services.py",
    clear_modules=("constants",),
)
sys.modules["services"] = api_services
api_router = load_module("api_router", API_PATH / "router.py")
sys.modules["router"] = api_router
api_handler = load_module("api_handler", API_PATH / "handler.py")
