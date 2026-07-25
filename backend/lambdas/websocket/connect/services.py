import os
import time
import boto3
from common.logger import log

TABLE_NAME = os.environ["CONNECTIONS_TABLE_NAME"]
CONNECTION_TTL_SECONDS = 60 * 60 * 24  # 24 hours

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)  # type: ignore


def save_connection(connection_id, user_id):
    expires_at = int(time.time()) + CONNECTION_TTL_SECONDS

    ctx = {
        "connectionId": connection_id,
        "userId": user_id,
        "expiresAt": expires_at,
    }

    table.put_item(Item=ctx)

    log("INFO", "WebSocket connection saved", ctx)
