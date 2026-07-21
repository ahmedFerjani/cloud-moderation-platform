def get_http_method(event):
    return event["requestContext"]["http"]["method"]


def get_path(event):
    return event["rawPath"]
