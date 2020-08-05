import pytest
from typing import Dict, Any
from mt4client import MT4Client
from mt4client.api import Symbol, Order, OrderType


@pytest.fixture(scope="function")
def order_params(symbol: Symbol) -> Dict[str, Any]:
    return {
        "symbol": symbol,
        "lots": symbol.min_lot
    }


def test_orders(mt4: MT4Client):
    orders = mt4.orders()
    assert isinstance(orders, list)
    print(f"Found {len(orders)} orders.")


def test_orders_historical(mt4: MT4Client):
    orders = mt4.orders_historical()
    assert isinstance(orders, list)
    print(f"Found {len(orders)} historical orders.")


def test_market_buy(mt4: MT4Client, symbol: Symbol, order_params: Dict[str, Any]) -> Order:
    # create market order using relative stops
    bid = symbol.tick().bid
    points = 50
    order_params["order_type"] = OrderType.OP_BUY
    order_params["sl_points"] = points
    order_params["tp_points"] = points
    order = mt4.order_send_market(**order_params)

    assert isinstance(order, Order)
    assert order.order_type == OrderType.OP_BUY
    assert order.sl < bid
    assert order.tp > bid
    print(f"Order successful: {order}")
    return order


def test_market_sell(mt4: MT4Client, symbol: Symbol, order_params: Dict[str, Any]) -> Order:
    # create market order using absolute stops
    bid = symbol.tick().bid
    points = 100
    order_params["order_type"] = OrderType.OP_SELL
    order_params["sl"] = bid + points * symbol.point_size
    order_params["tp"] = bid - points * symbol.point_size
    order = mt4.order_send_market(**order_params)

    assert isinstance(order, Order)
    assert order.order_type == OrderType.OP_SELL
    assert order.sl > bid
    assert order.tp < bid
    print(f"Order successful: {order}")
    return order


def test_limit_buy(mt4: MT4Client, symbol: Symbol, order_params: Dict[str, Any]) -> Order:
    # create pending buy order with relative sl/tp
    optimistic_buy_price = symbol.tick().ask / 2
    order_params["order_type"] = OrderType.OP_BUYLIMIT
    order_params["price"] = optimistic_buy_price
    order_params["slippage"] = 1
    order_params["sl_points"] = 100
    order_params["tp_points"] = 100
    order = mt4.order_send_pending(**order_params)

    assert isinstance(order, Order)
    assert order.order_type == OrderType.OP_BUYLIMIT
    print(f"Order successful: {order}")
    return order


def test_limit_sell(mt4: MT4Client, symbol: Symbol, order_params: Dict[str, Any]) -> Order:
    # create pending sell order with no sl/tp
    optimistic_sell_price = symbol.tick().bid * 2
    order_params["order_type"] = OrderType.OP_SELLLIMIT
    order_params["price"] = optimistic_sell_price
    order_params["slippage"] = 1
    order = mt4.order_send_pending(**order_params)

    assert isinstance(order, Order)
    assert order.order_type == OrderType.OP_SELLLIMIT
    print(f"Order successful: {order}")
    return order
