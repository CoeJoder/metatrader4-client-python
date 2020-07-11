from enum import Enum


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
