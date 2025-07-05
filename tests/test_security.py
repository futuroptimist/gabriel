import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gabriel.security import is_strong_password, sanitize_log_line


def test_is_strong_password():
    assert is_strong_password("Abcdef1g")  # nosec B101
    assert not is_strong_password("short")  # nosec B101
    assert not is_strong_password("alllowercase1")  # nosec B101
    assert not is_strong_password("ALLUPPERCASE1")  # nosec B101
    assert not is_strong_password("NoDigits")  # nosec B101


def test_sanitize_log_line():
    line = "User email is user@example.com in log"
    assert sanitize_log_line(line) == "User email is <redacted> in log"  # nosec B101
