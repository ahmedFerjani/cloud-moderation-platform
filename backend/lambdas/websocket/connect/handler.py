import json

from common.logger import log
from common.event_capture import capture_sample_event
from common.middleware import api_exception_handler
from service import save_connection


@api_exception_handler
def lambda_handler(event, context):

    capture_sample_event("websocket-connect", event, context)

    connection_id = event["requestContext"]["connectionId"]
    user_id = event["requestContext"]["authorizer"]["user_id"]

    log("INFO", "WebSocket $connect INVOKED")

    save_connection(connection_id, user_id)

    log("INFO", "WebSocket $connect COMPLETED")

    return {"statusCode": 200, "body": json.dumps({"message": "connected"})}
