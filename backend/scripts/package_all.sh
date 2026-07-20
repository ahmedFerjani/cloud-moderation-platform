#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"  # cd to scripts/

echo "Packaging all layers and lambdas..."
echo ""

bash package_layer_serverless_utils.sh
bash package_layer_image_processing.sh

bash package_lambda_api.sh
bash package_lambda_orchestrator.sh
bash package_lambda_dlq_handler.sh

bash package_websocket_connect.sh
bash package_websocket_disconnect.sh

echo ""
echo "All packages complete."