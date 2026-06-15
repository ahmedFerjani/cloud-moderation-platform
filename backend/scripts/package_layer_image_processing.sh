#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."  # cd to backend/

OUTPUT="packages/image-processing.zip"
REQUIREMENTS="layers/image_processing/requirements.txt"
STAGING="build/image_processing"
PYTHON_DIR="${STAGING}/python"

echo "Packaging image-processing layer..."

# clean start
rm -rf "${STAGING:?}"
mkdir -p "$PYTHON_DIR"

# install into python/ subfolder (required by Lambda layer structure)
pip install -r "$REQUIREMENTS" \
  -t "$PYTHON_DIR" \
  --platform manylinux2014_aarch64 \
  --only-binary=:all: \
  --python-version 3.14 \
  --upgrade

# zip
mkdir -p packages
rm -f "$OUTPUT"
(cd "$STAGING" && zip -r "$OLDPWD/$OUTPUT" python -x "*.pyc" "*__pycache__*" > /dev/null)

# cleanup
rm -rf "${STAGING:?}"

echo "Done: $OUTPUT"