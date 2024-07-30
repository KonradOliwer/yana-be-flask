from datetime import datetime


def timestamp_in_seconds() -> int:
    return int(datetime.now().timestamp())
