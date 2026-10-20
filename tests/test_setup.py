import pytest


def test_success():
    assert True


def test_fail():
    with pytest.raises(RuntimeError):
        raise RuntimeError
