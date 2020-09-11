import pytest
from mt4client import MT4Client
from mt4client.api import Symbol, OrderType, MT4Error
from mt4client.api.errors import MT4ErrorCode


def test_retry_on_error(mt4: MT4Client, symbol: Symbol):
    # this should raise ERR_INVALID_PRICE_PARAM
    invalid_price = -10.0
    try:
        order = mt4.order_send(
            symbol=symbol,
            lots=symbol.min_lot,
            order_type=OrderType.OP_BUYLIMIT,
            price=invalid_price
        )
        pytest.fail(f"Expected invalidly priced order to fail:\n\t{order}")
    except MT4Error as ex:
        if ex.error_code is MT4ErrorCode.ERR_INVALID_PRICE_PARAM:
            # resend the order with a valid price
            new_price = symbol.tick.ask
            order = mt4.order_send(
                symbol=symbol,
                lots=symbol.min_lot,
                order_type=OrderType.OP_BUYLIMIT,
                price=new_price
            )
            assert order is not None
            assert order.open_price == new_price
            print(f"Order resend was successful: {order}")
        else:
            pytest.fail(f"Expected ERR_INVALID_PRICE_PARAM error instead of:\n\t{ex}")
