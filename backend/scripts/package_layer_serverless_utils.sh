#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

OUTPUT="packages/serverless-utils.zip"
SOURCE="layers/serverless_utils/python"

echo "Packaging serverless-utils layer..."
mkdir -p packages
rm -f "$OUTPUT"
(cd "$SOURCE/.." && zip -r "../../$OUTPUT" python -x "*.pyc" "*__pycache__*" > /dev/null)

echo "Done: $OUTPUT"