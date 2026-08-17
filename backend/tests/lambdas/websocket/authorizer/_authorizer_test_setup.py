import os
import sys
from pathlib import Path

from helpers import ensure_sys_path, find_backend_root, load_module

BACKEND_ROOT = find_backend_root(Path(__file__))
COMMON_PATH = BACKEND_ROOT / "layers" / "serverless_utils" / "python"
AUTHORIZER_PATH = BACKEND_ROOT / "lambdas" / "websocket" / "authorizer"

ensure_sys_path((COMMON_PATH, AUTHORIZER_PATH))

os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("USER_POOL_ID", "us-east-1_example")
os.environ.setdefault("APP_CLIENT_ID", "app-client-123")

authorizer_services = load_module(
    "authorizer_services",
    AUTHORIZER_PATH / "services.py",
    clear_modules=("services",),
)
sys.modules["services"] = authorizer_services
authorizer_handler = load_module("authorizer_handler", AUTHORIZER_PATH / "handler.py")
