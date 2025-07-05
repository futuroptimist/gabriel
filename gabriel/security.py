"""Basic security helpers for Gabriel."""

import re
from typing import Pattern

_EMAIL_PATTERN: Pattern[str] = re.compile(r"[\w\.-]+@[\w\.-]+")


def is_strong_password(password: str) -> bool:
    """Return True if the password appears strong."""
    if len(password) < 8:
        return False
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_lower and has_upper and has_digit


def sanitize_log_line(line: str) -> str:
    """Redact email addresses from log lines."""
    return _EMAIL_PATTERN.sub("<redacted>", line)
