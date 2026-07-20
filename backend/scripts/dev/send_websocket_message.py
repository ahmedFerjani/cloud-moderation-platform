"""
Send messages to WebSocket clients.

This utility is used during development to validate
API Gateway WebSocket connectivity and message delivery.
"""

import json
import boto3

# Set your deployed WebSocket Management API endpoint
WEBSOCKET_ENDPOINT = "https://sci49mbp1g.execute-api.us-east-1.amazonaws.com/$default"
# Set the target client connection ID
CONNECTION_ID = "gUsdKc-FBQAYKEjxJA=="

message_payload = {"type": "test", "message": "Hello from test script!"}

client = boto3.client("apigatewaymanagementapi", endpoint_url=WEBSOCKET_ENDPOINT)

client.post_to_connection(
    ConnectionId=CONNECTION_ID,
    Data=json.dumps(message_payload).encode(),
)
