import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--network",
        action="store_true",
        default=False,
        help="included running (slow) network calls",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "network: mark test as performing network calls")


def pytest_runtest_setup(item):
    if "network" in item.keywords and not item.config.getoption("--network"):
        pytest.skip("test requires '--network' option to run")
