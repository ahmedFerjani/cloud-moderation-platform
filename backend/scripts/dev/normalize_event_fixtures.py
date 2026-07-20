"""Normalize low-risk noisy identifiers in captured event fixtures.

This keeps fixture structure realistic while making values stable across captures.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

UUID_RE = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)
SAMPLE_UUID = "00000000-0000-0000-0000-000000000000"
NORMALIZED_VALUE = "<normalized>"

NORMALIZED_KEYS = {
    "etag",
    "md5ofbody",
    "versionid",
    "sequencer",
    "configurationid",
}

SQS_ARN_PREFIX_RE = re.compile(r"^(arn:aws:sqs:[^:]+:[^:]+:).+$")
S3_BUCKET_ARN_PREFIX_RE = re.compile(r"^(arn:aws:s3:::).+$")


def normalize_string(value: str) -> str:
    """Apply generic string normalization rules."""

    return UUID_RE.sub(SAMPLE_UUID, value)


def normalize_arn(value: str) -> str:
    """Normalize ARN resource names while keeping service and region context."""

    sqs_match = SQS_ARN_PREFIX_RE.match(value)
    if sqs_match:
        return f"{sqs_match.group(1)}<normalized-resource>"

    s3_match = S3_BUCKET_ARN_PREFIX_RE.match(value)
    if s3_match:
        return f"{s3_match.group(1)}<normalized-bucket>"

    return value


def normalize_value(value: Any, key_name: str = "") -> Any:
    """Recursively normalize fixture fields that are noisy but non-sensitive."""

    if isinstance(value, dict):
        return {key: normalize_value(item, key) for key, item in value.items()}

    if isinstance(value, list):
        return [normalize_value(item) for item in value]

    normalized_key = key_name.lower()

    if isinstance(value, str):
        if normalized_key in NORMALIZED_KEYS:
            return NORMALIZED_VALUE

        if normalized_key in {"eventsourcearn", "deadletterqueuesourcearn", "arn"}:
            value = normalize_arn(value)

        if normalized_key == "name" and value.startswith("image-labels-"):
            return "<normalized-bucket>"

        if normalized_key == "key" and value.startswith("uploads/"):
            return "uploads/sample-image.jpg"

        return normalize_string(value)

    return value


def normalize_file(path: Path) -> bool:
    """Normalize one JSON file. Returns True if file content changed."""

    original = path.read_text(encoding="utf-8")
    payload = json.loads(original)
    normalized = normalize_value(payload)
    updated = json.dumps(normalized, indent=2) + "\n"

    if updated == original:
        return False

    path.write_text(updated, encoding="utf-8")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--events-dir",
        default="backend/events",
        help="Directory containing JSON fixture files (default: backend/events)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    events_dir = Path(args.events_dir)

    if not events_dir.exists() or not events_dir.is_dir():
        raise SystemExit(f"Events directory not found: {events_dir}")

    changed = 0

    for path in sorted(events_dir.glob("*.json")):
        if normalize_file(path):
            changed += 1
            print(f"normalized: {path}")

    print(f"done: {changed} file(s) updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
