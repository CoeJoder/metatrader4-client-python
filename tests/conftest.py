"""Pytest config for integration tests."""

import pytest
from mt4client.client import MT4Client


@pytest.fixture(scope='session', autouse=True)
def mt4() -> MT4Client:
    return MT4Client(host="win10", push_port=28281, pull_port=28282, verbose=False)