from common.logger import log
from common.event_capture import capture_sample_event
from common.middleware import api_exception_handler
from services import verify_token


def _policy(principal_id, effect, resource, context=None):
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": resource,
                }
            ],
        },
        "context": context or {},
    }


@api_exception_handler
def lambda_handler(event, context):

    capture_sample_event("websocket-authorizer", event, context)

    token = (event.get("queryStringParameters") or {}).get("token")
    method_arn = event["methodArn"]

    if not token:
        log("WARN", "WebSocket connect rejected: no token provided", {})
        return _policy("anonymous", "Deny", method_arn)

    try:
        claims = verify_token(token)
    except Exception as e:
        log("WARN", "WebSocket connect rejected: token validation failed", {"error": repr(e)})
        return _policy("anonymous", "Deny", method_arn)

    log("INFO", "WebSocket connect authorized", {"userId": claims["sub"]})
    return _policy(claims["sub"], "Allow", method_arn, context={"user_id": claims["sub"]})
