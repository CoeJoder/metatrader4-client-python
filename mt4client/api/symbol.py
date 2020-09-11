from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Union, List
from mt4client.api import StandardTimeframe, NonStandardTimeframe, parse_timeframe, OHLCV

if TYPE_CHECKING:
    from mt4client.client import MT4Client


class MarketInfo(Enum):
    """MetaTrader 4 market information identifiers, used with MarketInfo() function.

    References:
        https://docs.mql4.com/constants/environment_state/marketinfoconstants
    """
    MODE_LOW = 1
    MODE_HIGH = 2
    MODE_TIME = 5
    MODE_BID = 9
    MODE_ASK = 10
    MODE_POINT = 11
    MODE_DIGITS = 12
    MODE_SPREAD = 13
    MODE_STOPLEVEL = 14
    MODE_LOTSIZE = 15
    MODE_TICKVALUE = 16
    MODE_TICKSIZE = 17
    MODE_SWAPLONG = 18
    MODE_SWAPSHORT = 19
    MODE_STARTING = 20
    MODE_EXPIRATION = 21
    MODE_TRADEALLOWED = 22
    MODE_MINLOT = 23
    MODE_LOTSTEP = 24
    MODE_MAXLOT = 25
    MODE_SWAPTYPE = 26
    MODE_PROFITCALCMODE = 27
    MODE_MARGINCALCMODE = 28
    MODE_MARGININIT = 29
    MODE_MARGINMAINTENANCE = 30
    MODE_MARGINHEDGED = 31
    MODE_MARGINREQUIRED = 32
    MODE_FREEZELEVEL = 33
    MODE_CLOSEBY_ALLOWED = 34


class SymbolInfoInteger(Enum):
    """MetaTrader 4 market symbol properties which return an integer.

    References:
        https://docs.mql4.com/constants/environment_state/marketinfoconstants#enum_symbol_info_integer
    """
    SYMBOL_SELECT = 0
    SYMBOL_VISIBLE = 76
    SYMBOL_SESSION_DEALS = 56               # MQL5 only
    SYMBOL_SESSION_BUY_ORDERS = 60          # MQL5 only
    SYMBOL_SESSION_SELL_ORDERS = 62         # MQL5 only
    SYMBOL_VOLUME = 10                      # MQL5 only
    SYMBOL_VOLUMEHIGH = 11                  # MQL5 only
    SYMBOL_VOLUMELOW = 12                   # MQL5 only
    SYMBOL_TIME = 15
    SYMBOL_DIGITS = 17
    SYMBOL_SPREAD_FLOAT = 41
    SYMBOL_SPREAD = 18
    SYMBOL_TRADE_CALC_MODE = 29
    SYMBOL_TRADE_MODE = 30
    SYMBOL_START_TIME = 51
    SYMBOL_EXPIRATION_TIME = 52
    SYMBOL_TRADE_STOPS_LEVEL = 31
    SYMBOL_TRADE_FREEZE_LEVEL = 32
    SYMBOL_TRADE_EXEMODE = 33
    SYMBOL_SWAP_MODE = 37
    SYMBOL_SWAP_ROLLOVER3DAYS = 40
    SYMBOL_EXPIRATION_MODE = 49             # MQL5 only
    SYMBOL_FILLING_MODE = 50                # MQL5 only
    SYMBOL_ORDER_MODE = 71                  # MQL5 only


class SymbolCalcMode(Enum):
    """The contract price calculation mode.

    This is the MQL4 version; the MQL5 enum has more members and possibly different index values.

    References:
        https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants#enum_symbol_calc_mode
        https://docs.mql4.com/convert/stringformat
    """
    SYMBOL_CALC_MODE_FOREX = 0
    SYMBOL_CALC_MODE_CFD = 1
    SYMBOL_CALC_MODE_FUTURES = 2
    SYMBOL_CALC_MODE_CFDINDEX = 3


class SymbolTradeMode(Enum):
    """MetaTrader 4 market symbol trading mode.

    References:
        https://docs.mql4.com/constants/environment_state/marketinfoconstants#enum_symbol_trade_mode
    """
    SYMBOL_TRADE_MODE_DISABLED = 0
    SYMBOL_TRADE_MODE_LONGONLY = 3          # MQL5 only
    SYMBOL_TRADE_MODE_SHORTONLY = 4         # MQL5 only
    SYMBOL_TRADE_MODE_CLOSEONLY = 1
    SYMBOL_TRADE_MODE_FULL = 2


class SymbolTradeExecution(Enum):
    """MetaTrader 4 market symbol deal execution modes.

    References:
        https://docs.mql4.com/constants/environment_state/marketinfoconstants#enum_symbol_trade_execution
    """
    SYMBOL_TRADE_EXECUTION_REQUEST = 0
    SYMBOL_TRADE_EXECUTION_INSTANT = 1
    SYMBOL_TRADE_EXECUTION_MARKET = 2
    SYMBOL_TRADE_EXECUTION_EXCHANGE = 3     # MQL5 only


class SymbolSwapMode(Enum):
    """The method of swap calculation.

    This is the MQL4 version; the MQL5 enum has more members and possibly different index values.

    References:
        https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants#enum_symbol_swap_mode
        https://docs.mql4.com/convert/stringformat
    """
    SYMBOL_SWAP_MODE_POINTS = 0
    SYMBOL_SWAP_MODE_CURRENCY_SYMBOL = 1
    SYMBOL_SWAP_MODE_INTEREST_CURRENT = 2
    SYMBOL_SWAP_MODE_CURRENCY_MARGIN = 3


class DayOfWeek(Enum):
    """Days of the week.

    References:
        https://docs.mql4.com/constants/environment_state/marketinfoconstants#enum_day_of_week
    """
    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6


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

        self.stop_level = stop_level
        """The stop level in points."""

        self.freeze_level = freeze_level
        """The order freeze level in points."""

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
        }, default=[])
        return [OHLCV(**bar) for bar in bars]

    @property
    def tick(self) -> SymbolTick:
        """
        The latest market prices of this symbol.

        References:
            https://docs.mql4.com/constants/structures/mqltick

        :return:    The latest symbol tick.
        """
        resp = self._mt4._get_response(request={
            "action": "GET_SYMBOL_TICK",
            "symbol": self.name
        })
        return SymbolTick(**resp)

    @property
    def is_selected(self) -> bool:
        """Whether symbol selected in Market Watch.

        Some symbols can be hidden in Market Watch, but still they are considered as selected.

        :return:    `SymbolInfoInteger(:symbol, SYMBOL_SELECT)`
        """
        return self._get_symbol_info_integer(SymbolInfoInteger.SYMBOL_SELECT)

    @property
    def is_visible(self) -> bool:
        """Whether symbol is visible in Market Watch.

        Some symbols (mostly, these are cross rates required for calculation of margin requirements or profits in
        deposit currency) are selected automatically, but generally are not visible in Market Watch.
        To be displayed such symbols have to be explicitly selected.

        :return:    `SymbolInfoInteger(:symbol, SYMBOL_VISIBLE)`
        """
        return self._get_symbol_info_integer(SymbolInfoInteger.SYMBOL_VISIBLE)

    @property
    def time(self) -> int:
        """Time of the last quote.

        :return:    `SymbolInfoInteger(:symbol, SYMBOL_TIME)`
        """
        return self._get_symbol_info_integer(SymbolInfoInteger.SYMBOL_TIME)

    @property
    def is_spread_float(self) -> bool:
        """Whether there is a floating spread.

        :return:    `SymbolInfoInteger(:symbol, SYMBOL_SPREAD_FLOAT)`
        """
        return self._get_symbol_info_integer(SymbolInfoInteger.SYMBOL_SPREAD_FLOAT)

    @property
    def spread(self) -> int:
        """Spread value in points.

        :return:    `SymbolInfoInteger(:symbol, SYMBOL_SPREAD)`
        """
        return self._get_symbol_info_integer(SymbolInfoInteger.SYMBOL_SPREAD)

    @property
    def trade_calc_mode(self) -> SymbolCalcMode:
        """Contract price calculation mode.

        :return:    `SymbolInfoInteger(:symbol, SYMBOL_TRADE_CALC_MODE)`
        """
        val = self._get_symbol_info_integer(SymbolInfoInteger.SYMBOL_TRADE_CALC_MODE)
        return SymbolCalcMode(val)

    @property
    def trade_mode(self) -> SymbolTradeMode:
        """Order execution type.

        :return:    `SymbolInfoInteger(:symbol, SYMBOL_TRADE_MODE)`
        """
        val = self._get_symbol_info_integer(SymbolInfoInteger.SYMBOL_TRADE_MODE)
        return SymbolTradeMode(val)

    @property
    def start_time(self) -> int:
        """Date of the symbol trade beginning (usually used for futures).

        :return:    `SymbolInfoInteger(:symbol, SYMBOL_START_TIME)`
        """
        return self._get_symbol_info_integer(SymbolInfoInteger.SYMBOL_START_TIME)

    @property
    def expiration_time(self) -> int:
        """Date of the symbol trade end (usually used for futures)

        :return:    `SymbolInfoInteger(:symbol, SYMBOL_EXPIRATION_TIME)`
        """
        return self._get_symbol_info_integer(SymbolInfoInteger.SYMBOL_EXPIRATION_TIME)

    @property
    def trade_stops_level(self) -> int:
        """Minimal indention in points from the current close price to place Stop orders.

        :return:    `SymbolInfoInteger(:symbol, SYMBOL_TRADE_STOPS_LEVEL)`
        """
        return self._get_symbol_info_integer(SymbolInfoInteger.SYMBOL_TRADE_STOPS_LEVEL)

    @property
    def trade_freeze_level(self) -> int:
        """Distance to freeze trade operations in points.

        :return:    `SymbolInfoInteger(:symbol, SYMBOL_TRADE_FREEZE_LEVEL)`
        """
        return self._get_symbol_info_integer(SymbolInfoInteger.SYMBOL_TRADE_FREEZE_LEVEL)

    @property
    def trade_exe_mode(self) -> SymbolTradeExecution:
        """Deal execution mode.

        :return:    `SymbolInfoInteger(:symbol, SYMBOL_TRADE_EXEMODE)`
        """
        val = self._get_symbol_info_integer(SymbolInfoInteger.SYMBOL_TRADE_EXEMODE)
        return SymbolTradeExecution(val)

    @property
    def swap_mode(self) -> SymbolSwapMode:
        """Swap calculation model.

        :return:    `SymbolInfoInteger(:symbol, SYMBOL_SWAP_MODE)`
        """
        val = self._get_symbol_info_integer(SymbolInfoInteger.SYMBOL_SWAP_MODE)
        return SymbolSwapMode(val)

    @property
    def swap_rollover3days(self) -> DayOfWeek:
        """Day of week to charge 3 days swap rollover.

        :return:    `SymbolInfoInteger(:symbol, SYMBOL_SWAP_ROLLOVER3DAYS)`
        """
        val = self._get_symbol_info_integer(SymbolInfoInteger.SYMBOL_SWAP_ROLLOVER3DAYS)
        return DayOfWeek(val)

    def _get_symbol_info_integer(self, prop: SymbolInfoInteger) -> Union[bool, int]:
        return self._mt4._get_response(request={
            "action": "GET_SYMBOL_INFO_INTEGER",
            "symbol": self.name,
            "property_name": prop.name
        })

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'name={self.name}, '
                f'point_size={self.point_size}, '
                f'digits={self.digits}, '
                f'lot_size={self.lot_size}, '
                f'tick_value={self.tick_value}, '
                f'tick_size={self.tick_size}, '
                f'min_lot={self.min_lot}, '
                f'lot_step={self.lot_step}, '
                f'max_lot={self.max_lot}, '
                f'freeze_level={self.freeze_level})')
