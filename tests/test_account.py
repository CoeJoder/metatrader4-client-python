"""Integration tests for the Account API."""

import pytest

from mt4client.api import Account, AccountTradeMode, AccountStopoutMode
from mt4client import MT4Client


@pytest.fixture(scope="module")
def account(mt4: MT4Client) -> Account:
    return mt4.account()


def test_account_login(account: Account):
    val = account.login
    assert isinstance(val, int)
    print(f"Account login: {val}")


def test_account_trade_mode(account: Account):
    val = account.trade_mode
    assert isinstance(val, AccountTradeMode)
    print(f"Account trade_mode: {val}")


def test_account_leverage(account: Account):
    val = account.leverage
    assert isinstance(val, int)
    print(f"Account leverage: {val}")


def test_account_limit_orders(account: Account):
    val = account.limit_orders
    assert isinstance(val, int)
    print(f"Account limit_orders: {val}")


def test_account_margin_so_mode(account: Account):
    val = account.margin_so_mode
    assert isinstance(val, AccountStopoutMode)
    print(f"Account margin_so_mode: {val}")


def test_account_trade_allowed(account: Account):
    val = account.trade_allowed
    assert isinstance(val, bool)
    print(f"Account trade_allowed: {val}")


def test_account_trade_expert(account: Account):
    val = account.trade_expert
    assert isinstance(val, int)
    print(f"Account trade_expert: {val}")


def test_account_balance(account: Account):
    val = account.balance
    assert isinstance(val, float)
    print(f"Account balance: {val}")


def test_account_credit(account: Account):
    val = account.credit
    assert isinstance(val, float)
    print(f"Account credit: {val}")


def test_account_profit(account: Account):
    val = account.profit
    assert isinstance(val, float)
    print(f"Account profit: {val}")


def test_account_equity(account: Account):
    val = account.equity
    assert isinstance(val, float)
    print(f"Account equity: {val}")


def test_account_margin(account: Account):
    val = account.margin
    assert isinstance(val, float)
    print(f"Account margin: {val}")


def test_account_margin_free(account: Account):
    val = account.margin_free
    assert isinstance(val, float)
    print(f"Account margin_free: {val}")


def test_account_margin_level(account: Account):
    val = account.margin_level
    assert isinstance(val, float)
    print(f"Account margin_level: {val}")


def test_account_margin_so_call(account: Account):
    val = account.margin_so_call
    assert isinstance(val, float)
    print(f"Account margin_so_call: {val}")


def test_account_margin_so_so(account: Account):
    val = account.margin_so_so
    assert isinstance(val, float)
    print(f"Account margin_so_so: {val}")


def test_account_name(account: Account):
    val = account.name
    assert isinstance(val, str)
    print(f"Account name: {val}")


def test_account_server(account: Account):
    val = account.server
    assert isinstance(val, str)
    print(f"Account server: {val}")


def test_account_currency(account: Account):
    val = account.currency
    assert isinstance(val, str)
    print(f"Account currency: {val}")


def test_account_company(account: Account):
    val = account.company
    assert isinstance(val, str)
    print(f"Account company: {val}")
