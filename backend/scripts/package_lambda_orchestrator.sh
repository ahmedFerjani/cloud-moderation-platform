#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

OUTPUT="packages/orchestrator.zip"
SOURCE="lambdas/orchestrator"

echo "Packaging orchestrator lambda..."
mkdir -p packages
rm -f "$OUTPUT"

(cd "$SOURCE" && zip -r "$OLDPWD/$OUTPUT" . -x "*.pyc" "*__pycache__*" "*.zip" > /dev/null)

echo "Done: $OUTPUT"