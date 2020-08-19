import zmq

from time import time, sleep
from threading import Thread
from typing import Any, Dict, List, Union
from mt4client.api import Account, MT4Error, Signal, Symbol, Order, OrderType


class MT4Client:
    """Client interface for a MetaTrader bridge.  The connection is established using reciprocal
    PUSH/PULL ZeroMQ sockets."""

    SOCKET_POLL_TIMEOUT = 1000

    def __init__(self, host: str = "localhost", protocol: str = "tcp", push_port: int = 28281, pull_port: int = 28282,
                 response_timeout: int = 10, response_poll_delay: int = 0.1, verbose: bool = False):
        """
        Constructor.  Initializes the ZeroMQ sockets and connects to the MT4 terminal.

        :param host:                    The hostname or IP address of the server running the MetaTrader terminal.
        :param protocol:                The socket protocol.
        :param push_port:               The PUSH port.  Must match the bridge's PULL port.
        :param pull_port:               The PULL port.  Must match the bridge's PUSH port.
        :param response_timeout:        The number of seconds to wait for a response after a request is made.
        :param response_poll_delay:     The response polling interval in seconds.
        :param verbose:                 Whether to print trace messages.
        """
        # the most recently PULL'd server response
        self._latest_response = None

        self._is_running = True
        self._verbose = verbose
        self._response_poll_delay = response_poll_delay
        self._response_timeout = response_timeout

        # create and configure the sockets
        self._context = zmq.Context()
        self._push_socket = self._context.socket(zmq.PUSH)
        self._push_socket.setsockopt(zmq.SNDHWM, 1)
        self._pull_socket = self._context.socket(zmq.PULL)
        self._pull_socket.setsockopt(zmq.RCVHWM, 1)

        # bind the sockets
        self._push_socket.connect(f"{protocol}://{host}:{push_port}")
        self._pull_socket.connect(f"{protocol}://{host}:{pull_port}")

        # create background thread to poll for server responses
        self._response_poller = Thread(target=self._poll_for_responses)
        self._response_poller.daemon = True
        self._response_poller.start()

    def shutdown(self):
        """Closes sockets, destroys ZeroMQ context, and kills polling thread."""
        self._print_trace("Disconnecting...")
        self._is_running = False
        if self._response_poller is not None:
            self._response_poller.join()

        # close all sockets immediately and terminate context
        self._context.destroy(0)

    def account(self) -> Account:
        """
        Get a query interface for the account details.

        :return:    The account object.
        """
        resp = self._get_response(request={"action": "GET_ACCOUNT_INFO"},
                                  timeout_message="Failed to fetch account")
        return Account(mt4=self, **resp)

    def symbol_names(self) -> List[str]:
        """
        Get the names of market symbols supported by the broker.

        :return:    A list of symbol names.
        """
        return self._get_response(request={"action": "GET_SYMBOLS"},
                                  timeout_message="Failed to fetch market symbol names",
                                  default=[])

    def symbols(self, *names: str) -> Dict[str, Symbol]:
        """
        Get query interfaces for market symbols.

        :param names:   The names of the symbols.
        :return:        A name-to-symbol dict of symbol objects.
        """
        resp = self._get_response(request={
            "action": "GET_SYMBOL_INFO",
            "names": names
        }, timeout_message=f"Failed to fetch symbols")
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
        }, timeout_message=f"Failed to fetch symbol")
        return Symbol(mt4=self, **resp[name])

    def signal_names(self) -> List[str]:
        """
        Get the names of all trading signals.

        :return:    A list of names of the available signals.
        """
        return self._get_response(request={"action": "GET_SIGNALS"},
                                  timeout_message="Failed to get trading signal names",
                                  default=[])

    def signals(self, *names: str) -> Dict[str, Signal]:
        """
        Get data for multiple trading signals.

        :param names:   The names of the signals.
        :return:        A name-to-signal dict of signal objects.
        """
        resp = self._get_response(request={
            "action": "GET_SIGNAL_INFO",
            "names": names
        }, timeout_message="Failed to get trading signals", default={})
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
        }, timeout_message="Failed to get trading signal", default={})
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
        }, timeout_message="Failed to run indicator")

    def orders(self) -> List[Order]:
        """
        Get the pending and open orders from the Trades tab.

        :return:    A list of open or pending Orders.
        """
        resp = self._get_response(request={
            "action": "GET_ORDERS"
        }, timeout_message="Failed to get orders", default=[])
        return [Order(**order_dict) for order_dict in resp]

    def orders_historical(self) -> List[Order]:
        """
        Get the deleted and closed orders from the Account History tab.

        :return:    A list of closed Orders.
        """
        resp = self._get_response(request={
            "action": "GET_HISTORICAL_ORDERS"
        }, timeout_message="Failed to get orders", default=[])
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
        }, timeout_message="Failed to get order")
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
        }, timeout_message="Failed to send order")
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
        }, timeout_message="Failed to modify order")
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
        }, timeout_message="Failed to close order")

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
        }, timeout_message="Failed to delete order")

    def _get_response(self, request: Dict[str, Any], timeout_message: str = "Timed out.", default: Any = None) -> Any:
        """
        Send a request object to the server and waits for a response.

        :param request:         The request to send.  Must have an `action` property.
        :param timeout_message: The message to raise if response times out.
        :param default:         The default return value.
        :return:                The server response or the default value if response is empty.
        """
        self._latest_response = None
        self._send_object(request)

        # poll for response
        start = time()
        while self._latest_response is None:
            sleep(self._response_poll_delay)
            if (time() - start) > self._response_timeout:
                break
        if self._latest_response is None:
            raise TimeoutError(timeout_message)

        # raise any errors
        resp = self._latest_response
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

    def _send_object(self, message: Dict[str, Any]):
        """
        Send a request object to the server, serialized as JSON.

        :param message: The request to send MetaTrader.  Must have an `action` property.
        """
        if self._push_socket.poll(MT4Client.SOCKET_POLL_TIMEOUT, zmq.POLLOUT):
            try:
                self._push_socket.send_json(message, zmq.DONTWAIT)
                self._print_trace(f"Request:  {message}")
            except zmq.ZMQError as e:
                self._print_exception(e)

    def _poll_for_responses(self):
        """Background task.  Polls the pull-socket for JSON responses sent by MetaTrader."""
        while self._is_running:
            if self._pull_socket.poll(MT4Client.SOCKET_POLL_TIMEOUT, zmq.POLLIN):
                try:
                    response = self._pull_socket.recv_json(zmq.DONTWAIT)
                    if response is not None:
                        self._print_trace(f"Response: {response}")
                        self._latest_response = response
                except zmq.ZMQError as e:
                    self._print_exception(e)

    def _print_trace(self, message: str):
        if self._verbose:
            print(f"[MT4-ZMQ] {message}")

    @staticmethod
    def _print_exception(ex: Exception):
        print(f"[MT4-ZMQ ERROR] {ex}")
