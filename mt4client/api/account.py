from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mt4client.client import MT4Client


class AccountInfoInteger(Enum):
    """
    MetaTrader 4 account properties which return an integer.

    References:
          https://docs.mql4.com/constants/environment_state/accountinformation#enum_account_info_integer
    """
    ACCOUNT_LOGIN = 0
    ACCOUNT_TRADE_MODE = 32
    ACCOUNT_LEVERAGE = 35
    ACCOUNT_LIMIT_ORDERS = 47
    ACCOUNT_MARGIN_SO_MODE = 44
    ACCOUNT_TRADE_ALLOWED = 33
    ACCOUNT_TRADE_EXPERT = 34


class AccountInfoDouble(Enum):
    """MetaTrader 4 account properties which return a double.

    References:
        https://docs.mql4.com/constants/environment_state/accountinformation#enum_account_info_double
    """
    ACCOUNT_BALANCE = 37
    ACCOUNT_CREDIT = 38
    ACCOUNT_PROFIT = 39
    ACCOUNT_EQUITY = 40
    ACCOUNT_MARGIN = 41
    ACCOUNT_MARGIN_FREE = 42
    ACCOUNT_MARGIN_LEVEL = 43
    ACCOUNT_MARGIN_SO_CALL = 45
    ACCOUNT_MARGIN_SO_SO = 46
    ACCOUNT_MARGIN_INITIAL = 48         # deprecated
    ACCOUNT_MARGIN_MAINTENANCE = 49     # deprecated
    ACCOUNT_ASSETS = 50                 # deprecated
    ACCOUNT_LIABILITIES = 51            # deprecated
    ACCOUNT_COMMISSION_BLOCKED = 52     # deprecated


class AccountStopoutMode(Enum):
    """
    MetaTrader 4 account's stop out mode.

    References:
        https://docs.mql4.com/constants/environment_state/accountinformation#enum_account_stopout_mode
    """
    ACCOUNT_STOPOUT_MODE_PERCENT = 0
    ACCOUNT_STOPOUT_MODE_MONEY = 1


class AccountTradeMode(Enum):
    """
    MetaTrader 4 account type.

    References:
        https://docs.mql4.com/constants/environment_state/accountinformation#enum_account_trade_mode
    """
    ACCOUNT_TRADE_MODE_DEMO = 0
    ACCOUNT_TRADE_MODE_CONTEST = 1
    ACCOUNT_TRADE_MODE_REAL = 2


class Account:
    """A MetaTrader 4 account."""

    def __init__(self, mt4: MT4Client, login: int, trade_mode: int, name: str, server: str, currency: str,
                 company: str):
        self._mt4 = mt4

        self.login = login
        """The account number."""

        self.trade_mode: AccountTradeMode = AccountTradeMode(trade_mode)
        """Account trade mode."""

        self.name = name
        """Client name."""

        self.server = server
        """Trade server name."""

        self.currency = currency
        """Account currency."""

        self.company = company
        """Name of a company that serves the account."""

    @property
    def leverage(self) -> int:
        """Account leverage."""
        return self._get_account_info_integer(AccountInfoInteger.ACCOUNT_LEVERAGE)

    @property
    def limit_orders(self) -> int:
        """Maximum allowed number of open positions and active pending orders (in total), 0 = unlimited."""
        return self._get_account_info_integer(AccountInfoInteger.ACCOUNT_LIMIT_ORDERS)

    @property
    def margin_so_mode(self) -> AccountStopoutMode:
        """Mode for setting the minimal allowed margin."""
        val = self._get_account_info_integer(AccountInfoInteger.ACCOUNT_MARGIN_SO_MODE)
        return AccountStopoutMode(val)

    @property
    def trade_allowed(self) -> bool:
        """Allowed trade for the current account."""
        val = self._get_account_info_integer(AccountInfoInteger.ACCOUNT_TRADE_ALLOWED)
        return bool(val)

    @property
    def trade_expert(self) -> int:
        """Allowed trade for an Expert Advisor."""
        val = self._get_account_info_integer(AccountInfoInteger.ACCOUNT_TRADE_EXPERT)
        return bool(val)

    @property
    def balance(self) -> float:
        """Account balance in the deposit currency."""
        return self._get_account_info_double(AccountInfoDouble.ACCOUNT_BALANCE)

    @property
    def credit(self) -> float:
        """Account credit in the deposit currency."""
        return self._get_account_info_double(AccountInfoDouble.ACCOUNT_CREDIT)

    @property
    def profit(self) -> float:
        """Current profit of an account in the deposit currency."""
        return self._get_account_info_double(AccountInfoDouble.ACCOUNT_PROFIT)

    @property
    def equity(self) -> float:
        """Account equity in the deposit currency."""
        return self._get_account_info_double(AccountInfoDouble.ACCOUNT_EQUITY)

    @property
    def margin(self) -> float:
        """Account margin used in the deposit currency."""
        return self._get_account_info_double(AccountInfoDouble.ACCOUNT_MARGIN)

    @property
    def margin_free(self) -> float:
        """Free margin of an account in the deposit currency."""
        return self._get_account_info_double(AccountInfoDouble.ACCOUNT_MARGIN_FREE)

    @property
    def margin_level(self) -> float:
        """Account margin level in percents."""
        return self._get_account_info_double(AccountInfoDouble.ACCOUNT_MARGIN_LEVEL)

    @property
    def margin_so_call(self) -> float:
        """Margin call level. Depending on :attr:`margin_level`, this is expressed in percents or in
        the deposit currency.
        """
        return self._get_account_info_double(AccountInfoDouble.ACCOUNT_MARGIN_SO_CALL)

    @property
    def margin_so_so(self) -> float:
        """Margin stop out level. Depending on the :attr:`margin_so_mode`, this is expressed in percents or in
        the deposit currency.
        """
        return self._get_account_info_double(AccountInfoDouble.ACCOUNT_MARGIN_SO_SO)

    def _get_account_info_integer(self, prop: AccountInfoInteger) -> int:
        return self._mt4._get_response(request={
            "action": "GET_ACCOUNT_INFO_INTEGER",
            "property_id": prop.value
        })

    def _get_account_info_double(self, prop: AccountInfoDouble) -> float:
        return self._mt4._get_response(request={
            "action": "GET_ACCOUNT_INFO_DOUBLE",
            "property_id": prop.value
        })

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'login={self.login}, '
                f'trade_mode={self.trade_mode}, '
                f'name={self.name}, '
                f'server={self.server}, '
                f'currency={self.currency}, '
                f'company={self.company})')
