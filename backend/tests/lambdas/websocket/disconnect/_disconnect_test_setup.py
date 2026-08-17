import os
import sys
from pathlib import Path

from helpers import ensure_sys_path, find_backend_root, load_module

BACKEND_ROOT = find_backend_root(Path(__file__))
COMMON_PATH = BACKEND_ROOT / "layers" / "serverless_utils" / "python"
DISCONNECT_PATH = BACKEND_ROOT / "lambdas" / "websocket" / "disconnect"

ensure_sys_path((COMMON_PATH, DISCONNECT_PATH))

os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("CONNECTIONS_TABLE_NAME", "test-connections-table")

disconnect_services = load_module(
    "disconnect_services",
    DISCONNECT_PATH / "services.py",
    clear_modules=("services",),
)
sys.modules["services"] = disconnect_services
disconnect_handler = load_module("disconnect_handler", DISCONNECT_PATH / "handler.py")
