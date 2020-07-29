from mt4client.api import AccountTradeMode


class Signal:
    """A trading signal in MetaTrader 4.

    References:
        https://docs.mql4.com/signals

        https://docs.mql4.com/constants/tradingconstants/signalproperties
    """

    def __init__(self, author_login: str, broker: str, broker_server: str, name: str,
                 currency: str, date_published: int, date_started: int, id: int, leverage: int, pips: int, rating: int,
                 subscribers: int, trades: int, trade_mode: int, balance: float, equity: float, gain: float,
                 max_drawdown: float, price: float, roi: float):
        self.author_login = author_login
        """Author login."""

        self.broker = broker
        """Broker name (company)."""

        self.broker_server = broker_server
        """Broker server."""

        self.name = name
        """Signal name."""

        self.currency = currency
        """Signal base currency."""

        self.date_published = date_published
        """Publication date (date when it become available for subscription)."""

        self.date_started = date_started
        """Monitoring start date."""

        self.id = id
        """Signal ID."""

        self.leverage = leverage
        """Account leverage."""

        self.pips = pips
        """Profit in pips."""

        self.rating = rating
        """Position iin rating."""

        self.subscribers = subscribers
        """Number of subscribers."""

        self.trades = trades
        """Number of trades."""

        self.trade_mode = AccountTradeMode(trade_mode)
        """Account type."""

        self.balance = balance
        """Account balance."""

        self.equity = equity
        """Account equity."""

        self.gain = gain
        """Account gain."""

        self.max_drawdown = max_drawdown
        """Account maximum drawdown."""

        self.price = price
        """Signal subscription price."""

        self.roi = roi
        """Return on investment (%)."""

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'author_login={self.author_login}, '
                f'broker={self.broker}, '
                f'broker_server={self.broker_server}, '
                f'name={self.name}, '
                f'currency={self.currency}, '
                f'date_published={self.date_published}, '
                f'date_started={self.date_started}, '
                f'id={self.id}, '
                f'leverage={self.leverage}, '
                f'pips={self.pips}, '
                f'rating={self.rating}, '
                f'subscribers={self.subscribers}, '
                f'trades={self.trades}, '
                f'trade_mode={self.trade_mode!r}, '
                f'balance={self.balance}, '
                f'equity={self.equity}, '
                f'gain={self.gain}, '
                f'max_drawdown={self.max_drawdown}, '
                f'price={self.price}, '
                f'roi={self.roi})')
