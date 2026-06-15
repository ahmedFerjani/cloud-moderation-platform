#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

OUTPUT="packages/dlq_handler.zip"
SOURCE="lambdas/dlq_handler"

echo "Packaging dlq handler lambda..."
mkdir -p packages
rm -f "$OUTPUT"

(cd "$SOURCE" && zip -r "$OLDPWD/$OUTPUT" . -x "*.pyc" "*__pycache__*" "*.zip" > /dev/null)

echo "Done: $OUTPUT"