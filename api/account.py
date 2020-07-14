from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from client import MT4Client


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

    @classmethod
    def fetch(cls, mt4: MT4Client):
        """Fetches static data for the account and returns an instance of this class."""
        resp = mt4._get_response(request={
            "action": "GET_ACCOUNT_INFO"
        }, timeout_message="Failed to fetch account.")
        return cls(mt4=mt4, **resp)

    def __init__(self, mt4: MT4Client, login: int, trade_mode: int, name: str, server: str, currency: str,
                 company: str):
        self._mt4 = mt4

        self.login = login
        """The account number."""

        self.trade_mode = AccountTradeMode(trade_mode)
        """Account trade mode."""

        self.name = name
        """Client name."""

        self.server = server
        """Trade server name."""

        self.currency = currency
        """Account currency."""

        self.company = company
        """Name of a company that serves the account."""

