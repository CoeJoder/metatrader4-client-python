from enum import Enum


class OrderType(Enum):
    """The order types available in MetaTrader 4.

    Reference:
        https://docs.mql4.com/trading/ordertype

        https://www.mql5.com/en/forum/122847
    """

    OP_BUY = 0
    OP_SELL = 1
    OP_BUYLIMIT = 2
    OP_BUYSTOP = 3
    OP_SELLLIMIT = 4
    OP_SELLSTOP = 5
    # the following types are not for making orders; they represent special broker actions shown in Account History
    OP_BALANCE = 6
    OP_CREDIT = 7
    OP_REBATE = 8

    @property
    def is_buy(self) -> bool:
        """
        :return: Whether the order type is a buy offer.
        """
        return self == OrderType.OP_BUY or self == OrderType.OP_BUYLIMIT or self == OrderType.OP_BUYSTOP

    @property
    def is_sell(self) -> bool:
        """
        :return: Whether the order type is a sell offer.
        """
        return self == OrderType.OP_SELL or self == OrderType.OP_SELLLIMIT or self == OrderType.OP_SELLSTOP

    @property
    def is_market(self) -> bool:
        """
        :return:    Whether the order type is market.
        """
        return self == OrderType.OP_BUY or self == OrderType.OP_SELL

    @property
    def is_pending(self) -> bool:
        """
        :return: Whether the order type is pending.
        """
        return (self == OrderType.OP_BUYLIMIT or self == OrderType.OP_BUYSTOP or
                self == OrderType.OP_SELLLIMIT or self == OrderType.OP_SELLSTOP)

    def __str__(self) -> str:
        if self is OrderType.OP_BUY:
            return "MARKET-BUY"
        elif self is OrderType.OP_SELL:
            return "MARKET-SELL"
        elif self is OrderType.OP_BUYLIMIT:
            return "LIMIT-BUY"
        elif self is OrderType.OP_BUYSTOP:
            return "STOP-BUY"
        elif self is OrderType.OP_SELLLIMIT:
            return "LIMIT-SELL"
        elif self is OrderType.OP_SELLSTOP:
            return "STOP-SELL"
        elif self is OrderType.OP_BALANCE:
            return "BALANCE"
        elif self is OrderType.OP_CREDIT:
            return "CREDIT"
        elif self is OrderType.OP_REBATE:
            return "REBATE"
        else:
            return "UNKNOWN"


class Order:
    """Represents an order in MetaTrader 4.

    Reference:
        https://docs.mql4.com/trading
    """

    def __init__(self, ticket: int, magic_number: int, symbol: str, order_type: int, lots: float,
                 open_price: float, close_price: float, open_time: str, close_time: str, expiration: str,
                 sl: float, tp: float, profit: float, commission: float, swap: float, comment: str):
        self.ticket = ticket
        """The order ticket number."""

        self.magic_number = magic_number
        """The identifying (magic) number."""

        self.symbol = symbol
        """The symbol name."""

        self.order_type = OrderType(order_type)
        """The order type."""

        self.lots = lots
        """Amount of lots (trade volume)."""

        self.open_price = open_price
        """The open price."""

        self.close_price = close_price
        """The close price."""

        self.open_time = open_time
        """The open date/time."""

        self.close_time = close_time
        """The close date/time."""

        self.expiration = expiration
        """The expiration date/time."""

        self.sl = sl
        """The stop-loss."""

        self.tp = tp
        """The take-profit."""

        self.profit = profit
        """The net profit (without swaps or commissions). For open orders, it is the current
        unrealized profit. For closed orders, it is the fixed profit.
        """

        self.commission = commission
        """The calculated commission."""

        self.swap = swap
        """The swap value."""

        self.comment = comment
        """The comment."""

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"ticket={self.ticket}, "
                f"magic_number={self.magic_number}, "
                f"symbol={self.symbol}, "
                f"order_type={self.order_type}, "
                f"lots={self.lots}, "
                f"open_price={self.open_price}, "
                f"close_price={self.close_price}, "
                f"open_time={self.open_time}, "
                f"close_time={self.close_time}, "
                f"expiration={self.expiration}, "
                f"sl={self.sl}, "
                f"tp={self.tp}, "
                f"profit={self.profit}, "
                f"commission={self.commission}, "
                f"swap={self.swap}, "
                f"comment={self.comment})")
