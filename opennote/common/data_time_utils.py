from datetime import datetime


PAST_TIME_EXPIRE_AT_COOKIE_VALUE =  "Thu, 01 Jan 1970 00:00:00 GMT"

def timestamp_in_seconds() -> int:
    return int(datetime.now().timestamp())


def timestamp_to_cookie_expires_format(unix_timestamp: int) -> str:
    dt = datetime.utcfromtimestamp(unix_timestamp)
    return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")