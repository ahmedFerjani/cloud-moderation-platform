import os
import boto3
from common.logger import log

TABLE_NAME = os.environ["CONNECTIONS_TABLE_NAME"]

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)  # type: ignore


def delete_connection(connection_id):
    table.delete_item(Key={"connectionId": connection_id})

    log("INFO", "WebSocket connection deleted", {"connectionId": connection_id})
