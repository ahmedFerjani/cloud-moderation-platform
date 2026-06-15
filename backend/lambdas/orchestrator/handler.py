from common.logger import log
from common.event_capture import capture_sample_event
from common.middleware import worker_exception_handler
from processor import process_moderation_event


@worker_exception_handler
def lambda_handler(event, context):

    capture_sample_event("orchestrator", event, context)

    log("INFO", "Content moderation INVOKED")

    process_moderation_event(event)

    log("INFO", "Content moderation COMPLETED")
