from datetime import datetime, timedelta, timezone


def get_current_time(timezone_name: str) -> str:

    if timezone_name == "Asia/Shanghai":
        transformed_timezone=timezone(timedelta(hours=8))
    elif timezone_name == "UTC":
        transformed_timezone=timezone.utc
    else:
        raise ValueError("Unsupported timezone")
    actual_time = datetime.now(transformed_timezone)
    return actual_time.isoformat()