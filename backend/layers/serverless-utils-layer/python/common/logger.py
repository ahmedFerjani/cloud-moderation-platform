import json


def log(level: str, message: str, extra: dict[str, str | int] | None = None):

    log_data: dict[str, str | int] = {
        "level": level,
        "message": message,
    }

    if extra:
        log_data.update(extra)

    print(json.dumps(log_data))
