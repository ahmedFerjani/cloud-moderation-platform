"""Exception-handling decorators for API and worker Lambda handlers."""

import json
from typing import Callable, Any, Dict
from functools import wraps
from botocore.exceptions import ClientError
from common.logger import log
from common.responses import api_response
from common.exceptions import APPError

LambdaHandler = Callable[..., Any]


def api_exception_handler(func: LambdaHandler) -> LambdaHandler:

    @wraps(func)
    def wrapper(event: Dict[str, Any], context: Any) -> Dict[str, Any]:

        try:
            return func(event, context)

        except json.JSONDecodeError as e:

            log(
                "ERROR",
                "Request body contains invalid JSON",
                {
                    "error": repr(e),
                },
            )

            return api_response(
                400,
                {
                    "error": {
                        "code": "INVALID_JSON",
                        "message": "Invalid JSON request body",
                    }
                },
            )

        except APPError as e:

            log(
                "ERROR",
                e.message,
                {
                    "code": e.code,
                },
            )

            return api_response(
                e.status_code,
                {
                    "error": {
                        "code": e.code,
                        "message": e.message,
                    }
                },
            )

        except ClientError as e:

            log(
                "ERROR",
                "AWS service operation failed",
                {
                    "error": repr(e),
                },
            )

            return api_response(
                500,
                {
                    "error": {
                        "code": "AWS_SERVICE_ERROR",
                        "message": "A cloud service error occurred",
                    }
                },
            )

        except Exception as e:

            log(
                "ERROR",
                "Unhandled server exception",
                {
                    "error": repr(e),
                },
            )

            return api_response(
                500,
                {
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected server error occurred",
                    }
                },
            )

    return wrapper


def worker_exception_handler(func: LambdaHandler) -> LambdaHandler:

    @wraps(func)
    def wrapper(event: Dict[str, Any], context: Any) -> Dict[str, Any]:

        try:
            return func(event, context)

        except APPError as e:

            log(
                "ERROR",
                e.message,
                {
                    "code": e.code,
                },
            )

            raise e

        except ClientError as e:

            log(
                "ERROR",
                "AWS service operation failed",
                {
                    "error": repr(e),
                },
            )

            raise e

        except Exception as e:

            log(
                "ERROR",
                "Unhandled server exception",
                {
                    "error": repr(e),
                },
            )

            raise e

    return wrapper
