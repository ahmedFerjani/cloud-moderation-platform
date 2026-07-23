def get_http_method(event):
    return event["requestContext"]["http"]["method"]


def get_path(event):
    return event["rawPath"]


def get_cognito_jwt_sub(event):
    return event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
