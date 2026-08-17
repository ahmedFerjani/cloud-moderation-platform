import os
import sys
from pathlib import Path

from helpers import ensure_sys_path, find_backend_root, load_module

BACKEND_ROOT = find_backend_root(Path(__file__))
COMMON_PATH = BACKEND_ROOT / "layers" / "serverless_utils" / "python"
CONNECT_PATH = BACKEND_ROOT / "lambdas" / "websocket" / "connect"

ensure_sys_path((COMMON_PATH, CONNECT_PATH))

os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("CONNECTIONS_TABLE_NAME", "test-connections-table")

connect_services = load_module(
    "connect_services",
    CONNECT_PATH / "services.py",
    clear_modules=("services",),
)
sys.modules["services"] = connect_services
connect_handler = load_module("connect_handler", CONNECT_PATH / "handler.py")
