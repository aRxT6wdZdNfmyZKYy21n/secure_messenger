from datetime import (
    datetime,
    timezone
)

def get_aware_current_datetime() -> (
        datetime
):
    return (
        datetime.now(
            tz=(
                timezone.utc
            )
        )
    )


def get_aware_current_timestamp_ms() -> int:
    aware_current_datetime = (
        get_aware_current_datetime()
    )

    return (
        int(
            aware_current_datetime.timestamp() *
            1000.
        )
    )