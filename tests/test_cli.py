from gabriel.utils import main


def test_cli_add(capsys):
    main(["add", "2", "3"])
    assert capsys.readouterr().out.strip() == "5.0"  # nosec B101


def test_cli_sqrt(capsys):
    main(["sqrt", "9"])
    assert capsys.readouterr().out.strip() == "3.0"  # nosec B101
