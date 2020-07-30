"""Integration tests for the Symbol API."""

import pytest

from mt4client.api import Symbol
from mt4client import MT4Client


@pytest.fixture(scope="module")
def symbol(mt4: MT4Client, symbol_name: str) -> Symbol:
    return mt4.symbol(symbol_name)


def test_symbol_tick(symbol: Symbol):
    tick = symbol.tick()
    assert isinstance(tick.time, int)
    assert isinstance(tick.bid, float)
    assert isinstance(tick.ask, float)
    assert isinstance(tick.last, float)
    assert isinstance(tick.volume, int)


def test_fetch_market_info(symbol: Symbol):
    spread = int(symbol.market_info("MODE_SPREAD"))
    assert spread > 0


def test_fetch_ohlcv(symbol: Symbol):
    ohlcv = symbol.ohlcv("1h", 100)
    assert isinstance(ohlcv, list)
    assert len(ohlcv) == 100
    print(f"Found {len(ohlcv)} OHLCV bars. The first one: {ohlcv[0]}")
