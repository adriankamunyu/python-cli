import re

def validate_email(email: str) -> str:
    """Return cleaned email or raise ValueError."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    cleaned = email.strip().lower()
    if not re.match(pattern, cleaned):
        raise ValueError(f"'{email}' is not a valid email address.")
    return cleaned

def validate_date(date_str: str) -> str:
    """
    Accept dates in YYYY-MM-DD format.
    Returns the date string if valid, raises ValueError otherwise.
    """
    from dateutil import parser as dateparser
    try:
        parsed = dateparser.parse(date_str)
        return parsed.strftime("%Y-%m-%d")
    except (ValueError, TypeError) as exc:
        raise ValueError(
            f"'{date_str}' is not a recognisable date. Use YYYY-MM-DD."
        ) from exc

def validate_status(status: str) -> str:
    """Return normalised status string or raise ValueError."""
    allowed = {"pending", "in_progress", "complete"}
    s = status.strip().lower()
    if s not in allowed:
        raise ValueError(
            f"Status must be one of {sorted(allowed)}, got '{status}'."
        )
    return s
