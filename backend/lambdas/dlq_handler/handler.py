from common.logger import log
from common.event_capture import capture_sample_event
from common.middleware import worker_exception_handler
from processor import process_dlq_event


@worker_exception_handler
def lambda_handler(event, context):

    capture_sample_event("dlq_handler", event, context)

    log("INFO", "DLQ handler INVOKED")

    process_dlq_event(event)

    log("INFO", "DLQ handler COMPLETED")
