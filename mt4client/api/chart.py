from enum import Enum
from typing import Union
import re


class StandardTimeframe(Enum):
    """The standard timeframes available for chart data in MetaTrader 4.
    Online charts of financial instruments can be plotted only on these time intervals.

    Reference:
        https://docs.mql4.com/constants/chartconstants/enum_timeframes
    """
    PERIOD_CURRENT = 0
    PERIOD_M1 = 1
    PERIOD_M5 = 5
    PERIOD_M15 = 15
    PERIOD_M30 = 30
    PERIOD_H1 = 60
    PERIOD_H4 = 240
    PERIOD_D1 = 1440
    PERIOD_W1 = 10080
    PERIOD_MN1 = 43200

    @property
    def is_standard(self) -> bool:
        return True


class NonStandardTimeframe(Enum):
    """The non-standard timeframes available for chart data in MetaTrader 4.
    These periods can be used for working with offline charts.

    Reference:
        https://docs.mql4.com/constants/chartconstants/enum_timeframes
    """
    PERIOD_M2 = 2
    PERIOD_M3 = 3
    PERIOD_M4 = 4
    PERIOD_M6 = 6
    PERIOD_M10 = 10
    PERIOD_M12 = 12
    PERIOD_M20 = 20
    PERIOD_H2 = 120
    PERIOD_H3 = 180
    PERIOD_H6 = 360
    PERIOD_H8 = 480
    PERIOD_H12 = 720

    @property
    def is_standard(self) -> bool:
        return False


class OHLCV(object):
    """An OHLCV bar."""

    def __init__(self, open: int, high: int, low: int, close: int, tick_volume: int, time: int):
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.tick_volume = tick_volume
        self.time = time

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'open="{self.open}, '
                f'high={self.high}, '
                f'low={self.low}, '
                f'close={self.close}, '
                f'tick_volume={self.tick_volume}, '
                f'time={self.time})')


def parse_timeframe(timeframe: str) -> Union[StandardTimeframe, NonStandardTimeframe]:
    """
    Parses a timeframe string.  An exception is raised if timeframe is invalid or parsing fails.

    :param timeframe:   A timeframe string, eg. '10m', '4h', '1d', '1w', '1mn' etc.
    :return:            A valid timeframe object.
    """
    if timeframe == "0":
        return StandardTimeframe.PERIOD_CURRENT

    p = re.compile(r"(\d+)([mhdwn]+)", re.IGNORECASE)
    m = p.match(timeframe)
    if m is not None and len(m.groups()) == 2:
        name = "PERIOD_" + m.group(2).upper() + m.group(1)
        try:
            return StandardTimeframe[name]
        except KeyError:
            try:
                return NonStandardTimeframe[name]
            except KeyError:
                pass
    raise ValueError("Invalid timeframe: " + timeframe)
