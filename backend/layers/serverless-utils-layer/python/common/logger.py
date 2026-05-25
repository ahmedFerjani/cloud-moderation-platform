import json


def log(level: str, message: str, extra: dict[str, str] | None = None):

    log_data = {
        "level": level,
        "message": message,
    }

    if extra:
        log_data.update(extra)

    print(json.dumps(log_data))
