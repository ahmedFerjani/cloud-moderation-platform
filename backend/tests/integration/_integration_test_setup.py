import base64
import json
import os
import sys
from pathlib import Path

from helpers import ensure_sys_path, find_backend_root, load_event, load_module

TESTS_ROOT = Path(__file__).resolve().parents[1]
if str(TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(TESTS_ROOT))


BACKEND_ROOT = find_backend_root(Path(__file__))
COMMON_PATH = BACKEND_ROOT / "layers" / "serverless-utils-layer" / "python"
API_PATH = BACKEND_ROOT / "lambdas" / "content-moderation-api"
ORCHESTRATOR_PATH = BACKEND_ROOT / "lambdas" / "content-moderation-orchestrator"
DLQ_PATH = BACKEND_ROOT / "lambdas" / "content-moderation-dlq-handler"
EVENTS_PATH = BACKEND_ROOT / "events"

ensure_sys_path((DLQ_PATH, ORCHESTRATOR_PATH, API_PATH, COMMON_PATH))

os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("BUCKET_NAME", "test-bucket")
os.environ.setdefault("TABLE_NAME", "test-table")
os.environ.setdefault("SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:123456789012:test-topic")


# Reorders a path to the front so implicit imports resolve to the active lambda stack.
def prioritize_sys_path(path: Path) -> None:
    text = str(path)
    while text in sys.path:
        sys.path.remove(text)
    sys.path.insert(0, text)


# Loads API lambda modules as an isolated stack with correct import wiring.
def load_api_stack():
    prioritize_sys_path(API_PATH)
    api_services = load_module(
        "integration_api_services", API_PATH / "services.py", clear_modules=("constants",)
    )
    sys.modules["services"] = api_services
    api_router = load_module("integration_api_router", API_PATH / "router.py")
    sys.modules["router"] = api_router
    api_handler = load_module("integration_api_handler", API_PATH / "handler.py")
    return api_services, api_router, api_handler


# Loads orchestrator lambda modules as an isolated stack with correct import wiring.
def load_orchestrator_stack():
    prioritize_sys_path(ORCHESTRATOR_PATH)
    orchestrator_validation = load_module(
        "integration_orchestrator_validation",
        ORCHESTRATOR_PATH / "validation.py",
        clear_modules=("constants", "validation"),
    )
    sys.modules["validation"] = orchestrator_validation
    orchestrator_services = load_module(
        "services",
        ORCHESTRATOR_PATH / "services" / "__init__.py",
        clear_modules=("constants", "services"),
    )
    orchestrator_processor = load_module(
        "integration_orchestrator_processor", ORCHESTRATOR_PATH / "processor.py"
    )
    sys.modules["processor"] = orchestrator_processor
    orchestrator_handler = load_module(
        "integration_orchestrator_handler", ORCHESTRATOR_PATH / "handler.py"
    )
    return orchestrator_services, orchestrator_processor, orchestrator_handler


# Loads DLQ lambda modules as an isolated stack with correct import wiring.
def load_dlq_stack():
    prioritize_sys_path(DLQ_PATH)
    dlq_services = load_module("integration_dlq_services", DLQ_PATH / "services.py")
    sys.modules["services"] = dlq_services
    dlq_processor = load_module("integration_dlq_processor", DLQ_PATH / "processor.py")
    sys.modules["processor"] = dlq_processor
    dlq_handler = load_module("integration_dlq_handler", DLQ_PATH / "handler.py")
    return dlq_services, dlq_processor, dlq_handler


# Produces API Gateway-like runtime events by serializing fixture request bodies.
def api_runtime_event(name: str) -> dict:
    event = load_event(EVENTS_PATH, name)
    if isinstance(event.get("body"), dict):
        event["body"] = json.dumps(event["body"])
    return event


# Produces orchestrator SQS runtime events by serializing nested message bodies.
def orchestrator_runtime_event() -> dict:
    event = load_event(EVENTS_PATH, "orchestrator-sqs-event.json")
    for record in event["Records"]:
        if isinstance(record.get("body"), dict):
            record["body"] = json.dumps(record["body"])
    return event


# Produces compact DLQ failure events with optional hash overrides.
def dlq_runtime_event(error: str = "moved_to_dlq", image_hash: str | None = None) -> dict:
    event = load_event(EVENTS_PATH, "dlq-sqs-event.json")
    for record in event["Records"]:
        if isinstance(record.get("body"), dict):
            message = {
                "s3_key": record["body"]["Records"][0]["s3"]["object"]["key"],
                "error": error,
            }
            if image_hash is not None:
                message["image_hash"] = image_hash
            record["body"] = json.dumps(message)
    return event


# Builds a minimal Lambda context object with a deterministic request ID.
def runtime_context(request_id: str):
    return type("Ctx", (), {"aws_request_id": request_id})()


PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO7Z0Y4AAAAASUVORK5CYII="
)


# Mimics boto3 streaming body reads used by S3 get_object responses.
class FakeBody:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return self._payload


# In-memory S3 fake supporting presign, object reads, and deletes.
class FakeS3Client:
    def __init__(self, image_bytes: bytes | None = None) -> None:
        self.image_bytes = image_bytes or PNG_BYTES
        self.deleted_objects: list[tuple[str, str]] = []
        self.presigned_posts: list[dict] = []

    def generate_presigned_post(self, **kwargs):
        self.presigned_posts.append(kwargs)
        return {
            "url": "https://example-upload.test",
            "fields": {"key": kwargs["Key"], "Content-Type": kwargs["Fields"]["Content-Type"]},
        }

    def get_object(
        self,
        Bucket: str,
        Key: str,
        ExpectedBucketOwner: str | None = None,
    ):
        return {"Body": FakeBody(self.image_bytes)}

    def delete_object(
        self,
        Bucket: str,
        Key: str,
        ExpectedBucketOwner: str | None = None,
    ):
        self.deleted_objects.append((Bucket, Key))


# In-memory Rekognition fake that returns configurable moderation labels.
class FakeRekognitionClient:
    def __init__(self, labels: list[dict] | None = None) -> None:
        self.labels = labels or []

    def detect_moderation_labels(self, **_kwargs):
        return {"ModerationLabels": self.labels}


# In-memory Textract fake that returns configurable block payloads.
class FakeTextractClient:
    def __init__(self, blocks: list[dict] | None = None) -> None:
        self.blocks = blocks or []

    def detect_document_text(self, **_kwargs):
        return {"Blocks": self.blocks}


# In-memory Comprehend fake for language, sentiment, and PII analysis.
class FakeComprehendClient:
    def __init__(
        self,
        language_code: str = "en",
        sentiment: str = "NEUTRAL",
        sentiment_scores: dict | None = None,
        pii_entities: list[dict] | None = None,
        toxic_labels: list[dict] | None = None,
    ) -> None:
        self.language_code = language_code
        self.sentiment = sentiment
        self.sentiment_scores = sentiment_scores or {
            "Positive": 0.25,
            "Negative": 0.25,
            "Neutral": 0.45,
            "Mixed": 0.05,
        }
        self.pii_entities = pii_entities or []
        self.toxic_labels = toxic_labels or []

    def detect_dominant_language(self, **_kwargs):
        return {"Languages": [{"LanguageCode": self.language_code, "Score": 0.99}]}

    def detect_sentiment(self, **_kwargs):
        return {
            "Sentiment": self.sentiment,
            "SentimentScore": self.sentiment_scores,
        }

    def detect_pii_entities(self, **_kwargs):
        return {"Entities": self.pii_entities}

    def detect_toxic_content(self, **_kwargs):
        return {"ResultList": [{"Labels": self.toxic_labels}]}


# In-memory SNS fake that records published notification payloads.
class FakeSNSClient:
    def __init__(self) -> None:
        self.published_messages: list[dict] = []

    def publish(self, **kwargs):
        self.published_messages.append(kwargs)

    def last_message_body(self) -> dict:
        return json.loads(self.published_messages[-1]["Message"])


# In-memory DynamoDB table fake supporting get, scan, query, and put behaviors.
class FakeTable:
    def __init__(self, items: list[dict] | None = None, existing_item=None) -> None:
        self.items = items or []
        self.existing_item = existing_item
        self.put_items: list[dict] = []

    def get_item(self, Key: dict):
        item = next((item for item in self.items if item["image_id"] == Key["image_id"]), None)
        return {"Item": item} if item else {}

    def scan(self, Limit: int):
        items = self.items[:Limit]
        return {"Items": items, "Count": len(items)}

    def query(self, **_kwargs):
        return {"Items": [self.existing_item] if self.existing_item else []}

    def put_item(self, Item: dict):
        self.put_items.append(Item)
