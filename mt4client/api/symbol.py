from __future__ import annotations
from typing import TYPE_CHECKING
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

    def fetch_tick(self) -> SymbolTick:
        """Fetches the latest market prices of this symbol."""
        resp = self._mt4._get_response(request={
            "action": "GET_SYMBOL_TICK",
            "symbol": self.name
        }, timeout_message=f"Failed to get last tick for symbol: '{self.name}'")
        return SymbolTick(**resp)
