import json

from common.logger import log
from common.event_capture import capture_sample_event
from common.middleware import api_exception_handler
from service import delete_connection


@api_exception_handler
def lambda_handler(event, context):

    capture_sample_event("websocket-disconnect", event, context)

    connection_id = event["requestContext"]["connectionId"]

    log("INFO", "WebSocket $disconnect INVOKED")

    delete_connection(connection_id)

    log("INFO", "WebSocket $disconnect COMPLETED")

    return {"statusCode": 200, "body": json.dumps({"message": "disconnected"})}
