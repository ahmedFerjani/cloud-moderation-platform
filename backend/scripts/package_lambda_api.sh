#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

OUTPUT="packages/api.zip"
SOURCE="lambdas/api"

echo "Packaging api lambda..."
mkdir -p packages
rm -f "$OUTPUT"

(cd "$SOURCE" && zip -r "$OLDPWD/$OUTPUT" . -x "*.pyc" "*__pycache__*" "*.zip" > /dev/null)

echo "Done: $OUTPUT"