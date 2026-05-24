import pytest
from urdf_validator_main.cli import main


def test_main_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


def test_main_prints_not_implemented(capsys):
    with pytest.raises(SystemExit):
        main()
    captured = capsys.readouterr()
    assert "urdf_validate" in captured.out
