from mt4client import MT4Client
from mt4client.api import Symbol, Order, OrderType


def test_market_buy(mt4: MT4Client, symbol: Symbol) -> Order:
    # create a market order using relative stops
    bid = symbol.tick.bid
    points = 50
    order = mt4.order_send(
        symbol=symbol,
        lots=symbol.min_lot,
        order_type=OrderType.OP_BUY,
        sl_points=points,
        tp_points=points)

    assert isinstance(order, Order)
    assert order.order_type == OrderType.OP_BUY
    assert order.sl < bid
    assert order.tp > bid
    print(f"Order successful: {order}")
    return order


def test_market_sell(mt4: MT4Client, symbol: Symbol) -> Order:
    # create a market order using absolute stops
    bid = symbol.tick.bid
    points = 100
    sl = bid + points * symbol.point_size
    tp = bid - points * symbol.point_size
    order = mt4.order_send(
        symbol=symbol,
        lots=symbol.min_lot,
        order_type=OrderType.OP_SELL,
        sl=sl,
        tp=tp
    )

    assert isinstance(order, Order)
    assert order.order_type == OrderType.OP_SELL
    assert order.sl > bid
    assert order.tp < bid
    print(f"Order successful: {order}")
    return order


def test_limit_buy(mt4: MT4Client, symbol: Symbol) -> Order:
    # create a pending buy order with relative sl/tp
    optimistic_buy_price = symbol.tick.ask / 2
    slippage = 1
    sl_points = 100
    tp_points = 100
    order = mt4.order_send(
        symbol=symbol,
        lots=symbol.min_lot,
        order_type=OrderType.OP_BUYLIMIT,
        price=optimistic_buy_price,
        slippage=slippage,
        sl_points=sl_points,
        tp_points=tp_points
    )

    assert isinstance(order, Order)
    assert order.order_type == OrderType.OP_BUYLIMIT
    print(f"Order successful: {order}")
    return order


def test_limit_sell(mt4: MT4Client, symbol: Symbol) -> Order:
    # create a pending sell order with no sl/tp
    optimistic_sell_price = symbol.tick.bid * 2
    price = optimistic_sell_price
    slippage = 1
    order = mt4.order_send(
        symbol=symbol,
        lots=symbol.min_lot,
        order_type=OrderType.OP_SELLLIMIT,
        price=price,
        slippage=slippage
    )

    assert isinstance(order, Order)
    assert order.order_type == OrderType.OP_SELLLIMIT
    print(f"Order successful: {order}")
    return order


def test_modify_open_order(mt4: MT4Client, symbol: Symbol):
    # create a market order
    order = mt4.order_send(
        symbol=symbol,
        lots=symbol.min_lot,
        order_type=OrderType.OP_BUY
    )

    # add sl/tp stops
    bid = symbol.tick.bid
    points = 200
    sl = bid - points * symbol.point_size
    tp = bid + points * symbol.point_size

    # modify order
    order = mt4.order_modify(order=order, sl=sl, tp=tp)
    assert order.sl < bid
    assert order.tp > bid
    print(f"Order open_price/sl/tp: {order.open_price}/{order.sl}/{order.tp}")


def test_modify_pending_order(mt4: MT4Client, symbol: Symbol):
    # create a pending order
    optimistic_buy_price = symbol.tick.ask / 2
    slippage = 1
    sl_points = 100
    tp_points = 100
    order = mt4.order_send(
        symbol=symbol,
        lots=symbol.min_lot,
        order_type=OrderType.OP_BUYLIMIT,
        price=optimistic_buy_price,
        slippage=slippage,
        sl_points=sl_points,
        tp_points=tp_points
    )
    original_price = order.open_price

    # lower the price and widen the sl/tp windows
    new_price = original_price * 0.9
    new_points = 100

    # modify order
    order = mt4.order_modify(order=order, price=new_price, sl_points=new_points, tp_points=new_points)
    assert order.open_price < original_price
    assert order.sl < new_price
    assert order.tp > new_price
    print(f"Order open_price/sl/tp: {order.open_price}/{order.sl}/{order.tp}")


def test_close_open_order(mt4: MT4Client, symbol: Symbol):
    # create a market order
    order = mt4.order_send(
        symbol=symbol,
        lots=symbol.min_lot,
        order_type=OrderType.OP_BUY
    )

    # assert that the order was created and is open
    assert order is not None
    assert order.order_type.is_market

    # close the order
    mt4.order_close(order)
    search_results = [x for x in mt4.orders() if x.ticket == order.ticket]
    assert len(search_results) == 0
    print(f"Open order # {order.ticket} was closed.")


def test_close_pending_order(mt4: MT4Client, symbol: Symbol):
    # create a pending order
    optimistic_buy_price = symbol.tick.ask / 2
    order = mt4.order_send(
        symbol=symbol,
        lots=symbol.min_lot,
        order_type=OrderType.OP_BUYLIMIT,
        price=optimistic_buy_price
    )

    # assert that the order was created and is pending
    assert order is not None
    assert order.order_type.is_pending

    # close the order
    mt4.order_close(order)
    search_results = [x for x in mt4.orders() if x.ticket == order.ticket]
    assert len(search_results) == 0
    print(f"Open order # {order.ticket} was closed.")


def test_delete_pending_order(mt4: MT4Client, symbol: Symbol):
    # create a pending order
    optimistic_buy_price = symbol.tick.ask / 2
    order = mt4.order_send(
        symbol=symbol,
        lots=symbol.min_lot,
        order_type=OrderType.OP_BUYLIMIT,
        price=optimistic_buy_price
    )

    # assert that the order was created and is pending
    assert order is not None
    assert order.order_type.is_pending

    # delete the order
    mt4.order_close(order)
    search_results = [x for x in mt4.orders() if x.ticket == order.ticket]
    assert len(search_results) == 0
    print(f"Pending order # {order.ticket} was deleted.")


def test_orders(mt4: MT4Client):
    orders = mt4.orders()
    assert isinstance(orders, list)
    print(f"Found {len(orders)} orders.")


def test_orders_historical(mt4: MT4Client):
    orders = mt4.orders_historical()
    assert isinstance(orders, list)
    print(f"Found {len(orders)} historical orders.")


def test_close_all_orders(mt4: MT4Client):
    # close/delete all orders
    for order in mt4.orders():
        mt4.order_delete(order, close_if_opened=True)
    assert len(mt4.orders()) == 0
