import subprocess  # nosec B404
import sys


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-m", "gabriel.utils", *args]
    return subprocess.run(cmd, capture_output=True, text=True, check=True)  # nosec B603


def test_add_cli() -> None:
    result = run_cli("add", "2", "3")
    assert result.stdout.strip() == "5.0"  # nosec B101


def test_sqrt_cli() -> None:
    result = run_cli("sqrt", "9")
    assert result.stdout.strip() == "3.0"  # nosec B101
