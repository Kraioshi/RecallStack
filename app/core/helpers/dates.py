from datetime import UTC, datetime


def now() -> datetime:
    """Return the current UTC datetime as a timezone-aware object."""

    return datetime.now(UTC)
