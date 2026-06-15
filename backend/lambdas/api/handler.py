from common.logger import log
from common.event_capture import capture_sample_event
from common.middleware import api_exception_handler
from router import route_request


@api_exception_handler
def lambda_handler(event, context):

    capture_sample_event("api", event, context)

    log("INFO", "Content moderation API Lambda INVOKED")

    response = route_request(event)

    log("INFO", "Content moderation API Lambda COMPLETED")

    return response
