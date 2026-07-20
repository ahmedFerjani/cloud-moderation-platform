#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

OUTPUT="packages/websocket-disconnect.zip"
SOURCE="lambdas/websocket/disconnect"

echo "Packaging websocket disconnect lambda..."
mkdir -p packages
rm -f "$OUTPUT"

(cd "$SOURCE" && zip -r "$OLDPWD/$OUTPUT" . -x "*.pyc" "*__pycache__*" "*.zip" > /dev/null)

echo "Done: $OUTPUT"