#!/bin/bash
set -euo pipefail

# Resolve project root regardless of the current working directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PACKAGING_DIR="$PROJECT_ROOT/scripts/packaging"

cd "$PROJECT_ROOT"

echo "Packaging all layers and lambdas..."
echo ""

bash "$PACKAGING_DIR/package_layer_serverless_utils.sh"
bash "$PACKAGING_DIR/package_layer_image_processing.sh"

bash "$PACKAGING_DIR/package_lambda_api.sh"
bash "$PACKAGING_DIR/package_lambda_orchestrator.sh"
bash "$PACKAGING_DIR/package_lambda_dlq_handler.sh"

bash "$PACKAGING_DIR/package_websocket_connect.sh"
bash "$PACKAGING_DIR/package_websocket_disconnect.sh"

echo ""
echo "All packages complete."