"""Unit tests for chart-related functions."""

from mt4client.api import parse_timeframe, StandardTimeframe, NonStandardTimeframe


def test_parse_timeframe():
    assert parse_timeframe("15m") == StandardTimeframe.PERIOD_M15
    assert parse_timeframe("1h") == StandardTimeframe.PERIOD_H1
    assert parse_timeframe("1d") == StandardTimeframe.PERIOD_D1
    assert parse_timeframe("1w") == StandardTimeframe.PERIOD_W1
    assert parse_timeframe("1mn") == StandardTimeframe.PERIOD_MN1
    assert parse_timeframe("0") == StandardTimeframe.PERIOD_CURRENT
    assert parse_timeframe("2m") == NonStandardTimeframe.PERIOD_M2
    assert parse_timeframe("2h") == NonStandardTimeframe.PERIOD_H2

