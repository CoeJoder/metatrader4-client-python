import zmq

from typing import Any, Dict, List, Union
from mt4client.api import Account, MT4Error, Signal, Symbol, Order, OrderType


class MT4Client:
    """Client interface for the MetaTrader 4 Server."""

    def __init__(self, address: str = "tcp://localhost:28282", request_timeout_ms: int = 10000,
                 response_timeout_ms: int = 10000, verbose: bool = False):
        """
        Constructor.  Initialize the REQ socket and connect to the MT4 server.

        :param address:             The address of the server's listening socket.
        :param request_timeout_ms:  The number of milliseconds to wait for a request to be sent.
        :param response_timeout_ms: The number of milliseconds to wait for a response to be received.
        :param verbose:             Whether to print trace messages.
        """
        self._verbose = verbose

        # create and configure REQ socket
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REQ)
        self._socket.setsockopt(zmq.SNDHWM, 1)
        self._socket.setsockopt(zmq.RCVHWM, 1)
        self._socket.setsockopt(zmq.SNDTIMEO, request_timeout_ms)
        self._socket.setsockopt(zmq.RCVTIMEO, response_timeout_ms)

        # connect to server
        self._socket.connect(address)

    def shutdown(self):
        """Close all sockets immediately and terminate the ZeroMQ context."""
        self._print_trace("Disconnecting...")
        self._context.destroy(0)

    def account(self) -> Account:
        """
        Get a query interface for the account details.

        :return:    The account object.
        """
        resp = self._get_response(request={"action": "GET_ACCOUNT_INFO"})
        return Account(mt4=self, **resp)

    def symbol_names(self) -> List[str]:
        """
        Get the names of market symbols supported by the broker.

        :return:    A list of symbol names.
        """
        return self._get_response(request={"action": "GET_SYMBOLS"}, default=[])

    def symbols(self, *names: str) -> Dict[str, Symbol]:
        """
        Get query interfaces for market symbols.

        :param names:   The names of the symbols.
        :return:        A name-to-symbol dict of symbol objects.
        """
        resp = self._get_response(request={
            "action": "GET_SYMBOL_INFO",
            "names": names
        })
        return {name: Symbol(mt4=self, **resp[name]) for name in names}

    def symbol(self, name: str) -> Symbol:
        """
        Get a query interface for a market symbol.

        :param name:    The name of the symbol.
        :return:        The symbol object.
        """
        resp = self._get_response(request={
            "action": "GET_SYMBOL_INFO",
            "names": [name]
        })
        return Symbol(mt4=self, **resp[name])

    def signal_names(self) -> List[str]:
        """
        Get the names of all trading signals.

        :return:    A list of names of the available signals.
        """
        return self._get_response(request={"action": "GET_SIGNALS"}, default=[])

    def signals(self, *names: str) -> Dict[str, Signal]:
        """
        Get data for multiple trading signals.

        :param names:   The names of the signals.
        :return:        A name-to-signal dict of signal objects.
        """
        resp = self._get_response(request={
            "action": "GET_SIGNAL_INFO",
            "names": names
        }, default={})
        return {name: Signal(**resp[name]) for name in names}

    def signal(self, name: str) -> Signal:
        """
        Get data for a trading signal.

        :param name:    The name of the signal.
        :return:        The signal object.
        """
        resp = self._get_response(request={
            "action": "GET_SIGNAL_INFO",
            "names": [name]
        }, default={})
        return Signal(**resp[name])

    def indicator(self, func: str, args: List[Union[str, int, float]], timeout: int = 5000) -> float:
        """
        Run a built-in indicator function.

        References:
            https://docs.mql4.com/indicators

        :param func:    The name of the indicator function.
        :param args:    A list of function arguments.
        :param timeout: The maximum milliseconds to wait for the symbol's chart data to load.
        :return:        The numeric result.
        """
        return self._get_response(request={
            "action": "RUN_INDICATOR",
            "indicator": func,
            "argv": args,
            "timeout": timeout
        })

    def orders(self) -> List[Order]:
        """
        Get the pending and open orders from the Trades tab.

        :return:    A list of open or pending Orders.
        """
        resp = self._get_response(request={
            "action": "GET_ORDERS"
        }, default=[])
        return [Order(**order_dict) for order_dict in resp]

    def orders_historical(self) -> List[Order]:
        """
        Get the deleted and closed orders from the Account History tab.

        :return:    A list of closed Orders.
        """
        resp = self._get_response(request={
            "action": "GET_HISTORICAL_ORDERS"
        }, default=[])
        return [Order(**order_dict) for order_dict in resp]

    def order(self, ticket: int) -> Order:
        """
        Get an order by ticket number.  May be pending, open, or closed.

        :param ticket:  The ticket number.
        :return:        The Order object.
        """
        resp = self._get_response(request={
            "action": "GET_ORDER",
            "ticket": ticket
        })
        return Order(**resp)

    def order_send(self, symbol: Union[Symbol, str], order_type: OrderType, lots: float, price: float = None,
                   slippage: int = None, sl: float = None, tp: float = None, sl_points: int = None,
                   tp_points: int = None, comment: str = "") -> Order:
        """
        Create a new order.

        References:
            https://docs.mql4.com/trading/ordersend

            https://book.mql4.com/appendix/limits

        :param symbol:          The market symbol object or name.
        :param order_type:      The market order type.
        :param lots:            The number of lots to trade.
        :param price:           The desired open price.  Optional for market orders.
        :param slippage:        The maximum price slippage, in points.  Omit to use a permissive default (2.0 * spread).
        :param sl:              The absolute stop-loss to use.  Optional.
        :param tp:              The absolute take-profit to use.  Optional.
        :param sl_points:       The relative stop-loss to use, in points.  Optional.
        :param tp_points:       The relative take-profit to use, in points.  Optional.
        :param comment:         The order comment text.  Last part of the comment may be changed by server.  Optional.
        :return:                The new Order.
        """
        if not order_type.is_buy and not order_type.is_sell:
            raise ValueError("Invalid order type: " + str(order_type))
        if order_type.is_pending and price is None:
            raise ValueError("Pending orders must specify a price")
        resp = self._get_response(request={
            "action": "DO_ORDER_SEND",
            "symbol": symbol.name if isinstance(symbol, Symbol) else symbol,
            "order_type": order_type.value,
            "lots": lots,
            "price": price,
            "slippage": slippage,
            "sl": sl,
            "tp": tp,
            "sl_points": sl_points,
            "tp_points": tp_points,
            "comment": comment
        })
        return Order(**resp)

    def order_modify(self, order: Union[Order, int], price: float = None, sl: float = None, tp: float = None,
                     sl_points: int = None, tp_points: int = None) -> Order:
        """
        Modify a market or pending order.

        References:
            https://book.mql4.com/trading/ordermodify

            https://book.mql4.com/appendix/limits

        :param order:       An order or its ticket number.
        :param price:       The desired open price; applies to pending orders only.  Optional.
        :param sl:          The absolute stop-loss to use.  Optional.
        :param tp:          The absolute take-profit to use.  Optional.
        :param sl_points:   The relative stop-loss to use, in points.  Optional.
        :param tp_points:   The relative take-profit to use, in points.  Optional.
        :return:            The Order with the updated values.
        """
        resp = self._get_response(request={
            "action": "DO_ORDER_MODIFY",
            "ticket": order.ticket if isinstance(order, Order) else order,
            "price": price,
            "sl": sl,
            "tp": tp,
            "sl_points": sl_points,
            "tp_points": tp_points
        })
        return Order(**resp)

    def order_close(self, order: Union[Order, int]):
        """
        Close an open order.

        References:
            https://docs.mql4.com/trading/orderdelete

            https://book.mql4.com/appendix/limits

        :param order:   The order to close or its ticket number.
        """
        self._get_response(request={
            "action": "DO_ORDER_CLOSE",
            "ticket": order.ticket if isinstance(order, Order) else order
        })

    def order_delete(self, order: Union[Order, int], close_if_opened: bool = False):
        """
        Delete a pending order.

        References:
            https://docs.mql4.com/trading/orderdelete

            https://book.mql4.com/appendix/limits

        :param order:           The order to close or its ticket number.
        :param close_if_opened: If true and the order is open, it is closed at market price.  If false and the order is
                                open, an `ERR_INVALID_TICKET` error is raised.
        """
        self._get_response(request={
            "action": "DO_ORDER_DELETE",
            "closeIfOpened": close_if_opened,
            "ticket": order.ticket if isinstance(order, Order) else order
        })

    def _get_response(self, request: Dict[str, Any], default: Any = None) -> Any:
        """
        Send a request object to the server and wait for a response.

        :param request:         The request to send.  Must have an `action` property.
        :param default:         The default return value.
        :return:                The server response or the default value if response is empty.
        :raises:                zmq.ZMQError, MT4Error
        """
        self._socket.send_json(request)
        self._print_trace(f"Request:  {request}")
        resp = self._socket.recv_json()
        if resp is None:
            self._print_trace("Response is empty.")
        else:
            self._print_trace(f"Response: {resp}")

        # raise any errors
        error_code = resp.get("error_code")
        error_code_description = resp.get("error_code_description")
        error_message = resp.get("error_message")
        if not (error_code is None and error_code_description is None and error_message is None):
            raise MT4Error(error_code, error_code_description, error_message)

        # print any warnings to STDOUT
        warning_message = resp.get("warning")
        if warning_message is not None:
            print(str(warning_message))

        # unwrap the response
        return resp.get("response", default)

    def _print_trace(self, message: str):
        if self._verbose:
            print(f"[MT4-ZMQ] {message}")
