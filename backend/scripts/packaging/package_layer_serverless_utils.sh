#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

OUTPUT="packages/serverless-utils.zip"
SOURCE="layers/serverless_utils/python"

echo "Packaging serverless-utils layer..."
mkdir -p packages
rm -f "$OUTPUT"
(cd "$SOURCE/.." && zip -r "../../$OUTPUT" python -x "*.pyc" "*__pycache__*" > /dev/null)

echo "Done: $OUTPUT"