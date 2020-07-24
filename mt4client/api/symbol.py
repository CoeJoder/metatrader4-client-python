from __future__ import annotations
from typing import TYPE_CHECKING, Union, List
from mt4client.api import StandardTimeframe, NonStandardTimeframe, parse_timeframe, OHLCV

if TYPE_CHECKING:
    from mt4client.client import MT4Client


class SymbolTick:
    """The latest prices of a symbol in MetaTrader 4.

    Reference:
        https://docs.mql4.com/constants/structures/mqltick
    """

    def __init__(self, time: int, bid: float, ask: float, last: float, volume: int):
        self.time = time
        """The time of the last prices update."""

        self.bid = bid
        """The current bid price."""

        self.ask = ask
        """The current ask price."""

        self.last = last
        """The price of the last deal (Last)."""

        self.volume = volume
        """The volume for the current Last price."""

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"time={self.time}, "
                f"bid={self.bid}, "
                f"ask={self.ask}, "
                f"last={self.last}, "
                f"volume={self.volume})")


class Symbol:
    """A market symbol in MetaTrader 4.

    Reference:
        https://docs.mql4.com/constants/environment_state/marketinfoconstants
    """

    def __init__(self, mt4: MT4Client, name: str, point_size: float, digits: int, lot_size: float,
                 tick_value: float, tick_size: float, min_lot: float, lot_step: float, max_lot: float,
                 margin_init: float, margin_maintenance: float, margin_hedged: float, margin_required: float,
                 stop_level: float, freeze_level: float):
        self._mt4 = mt4

        self.name = name
        """The symbol name."""

        self.point_size = point_size
        """Point size in the quote currency."""

        self.digits = digits
        """The digits after the decimal point."""

        self.lot_size = lot_size
        """The lot size in the base currency."""

        self.tick_value = tick_value
        """The tick value in the deposit currency."""

        self.tick_size = tick_size
        """The tick size in points."""

        self.min_lot = min_lot
        """The minimum permitted amount of a lot."""

        self.lot_step = lot_step
        """The step for changing lots."""

        self.max_lot = max_lot
        """The maximum permitted amount of a lot."""

        self.margin_init = margin_init
        """The initial margin requirements for 1 lot."""

        self.margin_maintenance = margin_maintenance
        """The margin to maintain open orders calculated for 1 lot."""

        self.margin_hedged = margin_hedged
        """The hedged margin calculated for 1 lot."""

        self.margin_required = margin_required
        """The free margin required to open 1 lot for buying."""

        self.stop_level = stop_level
        """The stop level in points."""

        self.freeze_level = freeze_level
        """The order freeze level in points."""

    def tick(self) -> SymbolTick:
        """Get the latest market prices of this symbol."""
        resp = self._mt4._get_response(request={
            "action": "GET_SYMBOL_TICK",
            "symbol": self.name
        }, timeout_message=f"Failed to get last tick for symbol: '{self.name}'")
        return SymbolTick(**resp)

    def market_info(self, prop: str) -> Union[int, float, str]:
        """
        Fetches live market info about a symbol.

        References:
            https://docs.mql4.com/constants/environment_state/marketinfoconstants

        :param prop:    A valid property accepted by `MarketInfo(:property)`.  E.g. `MODE_SPREAD`
        :return:        The value returned by `MarketInfo(:property)`
        """
        return self._mt4._get_response(request={
            "action": "GET_SYMBOL_MARKET_INFO",
            "symbol": self.name,
            "property": prop
        }, timeout_message=f"Failed to get market info '{prop}' for symbol '{self.name}'")

    def ohlcv(self, timeframe: Union[str, StandardTimeframe, NonStandardTimeframe], limit: int = 100,
              timeout: int = 5000) -> List[OHLCV]:
        """
        Fetches OHLCV data for this symbol, up to the current time.

        :param timeframe:   The period.  Use a standard timeframe for a higher likelihood of success.
        :param limit:       The maximum number of bars to get.
        :param timeout:     The maximum milliseconds to wait for the broker's server to provide the requested data.
        :return:            A list of OHLCV bars, sorted oldest-to-newest, each having the following structure:
                            [time, open, high, low, close, volume]
        """
        period = parse_timeframe(timeframe).value if isinstance(timeframe, str) else timeframe.value
        bars = self._mt4._get_response(request={
            "action": "GET_OHLCV",
            "symbol": self.name,
            "timeframe": period,
            "limit": limit,
            "timeout": timeout
        }, timeout_message="Failed to get OHLCV data", default=[])
        return [OHLCV(**bar) for bar in bars]

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'name="{self.name}, '
                f'point_size={self.point_size}, '
                f'digits={self.digits}, '
                f'lot_size={self.lot_size}, '
                f'tick_value={self.tick_value}, '
                f'tick_size={self.tick_size}, '
                f'min_lot={self.min_lot}, '
                f'lot_step={self.lot_step}, '
                f'max_lot={self.max_lot}, '
                f'margin_init={self.margin_init}, '
                f'margin_maintenance={self.margin_maintenance}, '
                f'margin_hedged={self.margin_hedged}, '
                f'margin_required={self.margin_required}, '
                f'freeze_level={self.freeze_level})')
