from gabriel.utils import add, subtract


def test_add():
    assert add(1, 2) == 3  # nosec B101


def test_add_negative_numbers():
    assert add(-1, -2) == -3  # nosec B101


def test_subtract():
    assert subtract(5, 3) == 2  # nosec B101


def test_subtract_negative_result():
    assert subtract(3, 5) == -2  # nosec B101
