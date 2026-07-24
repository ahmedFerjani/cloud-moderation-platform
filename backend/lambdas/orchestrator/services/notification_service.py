import os
import json
import boto3
from botocore.exceptions import ClientError
from common.logger import log

CONNECTIONS_TABLE_NAME = os.environ["CONNECTIONS_TABLE_NAME"]
WEBSOCKET_ENDPOINT_URL = os.environ["WEBSOCKET_ENDPOINT_URL"]

dynamodb = boto3.resource("dynamodb")
connections_table = dynamodb.Table(CONNECTIONS_TABLE_NAME)  # type: ignore

apigw_management = boto3.client("apigatewaymanagementapi", endpoint_url=WEBSOCKET_ENDPOINT_URL)


def _get_connections_for_user(user_id):
    response = connections_table.query(
        IndexName="userId-index",
        KeyConditionExpression="userId = :uid",
        ExpressionAttributeValues={":uid": user_id},
    )
    return response.get("Items", [])


def notify_user(user_id, payload):
    if not user_id:
        log("WARN", "Skipping WebSocket notification: no user_id", {})
        return

    connections = _get_connections_for_user(user_id)

    if not connections:
        log("INFO", "No active WebSocket connections for user", {"userId": user_id})
        return

    message = json.dumps(payload).encode("utf-8")

    for conn in connections:
        connection_id = conn["connectionId"]
        try:
            apigw_management.post_to_connection(ConnectionId=connection_id, Data=message)
            log(
                "INFO",
                "WebSocket notification sent",
                {"connectionId": connection_id, "userId": user_id},
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "GoneException":
                log("WARN", "Stale WebSocket connection, removing", {"connectionId": connection_id})
                connections_table.delete_item(Key={"connectionId": connection_id})
            else:
                log(
                    "ERROR",
                    "Failed to send WebSocket notification",
                    {"connectionId": connection_id, "error": repr(e)},
                )
                raise
