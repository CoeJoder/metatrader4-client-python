"""Pytest config for integration tests."""

import pytest
from mt4client import MT4Client
from mt4client.api import Symbol


@pytest.fixture(scope="session", autouse=True)
def mt4() -> MT4Client:
    mt4 = MT4Client(address="tcp://win10:28282", verbose=False)
    yield mt4
    mt4.shutdown()


@pytest.fixture(scope="session", autouse=True)
def symbol_name() -> str:
    return "EURUSD"


@pytest.fixture(scope="session")
def symbol(mt4: MT4Client, symbol_name: str) -> Symbol:
    return mt4.symbol(symbol_name)
