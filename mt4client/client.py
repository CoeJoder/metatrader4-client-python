import zmq

from time import time, sleep
from threading import Thread
from typing import Any, Dict, List, Union
from mt4client.api import Account, MT4Error, Signal, Symbol


class MT4Client:
    """Client interface for a MetaTrader bridge.  The connection is established using reciprocal
    PUSH/PULL ZeroMQ sockets."""

    def __init__(self, host: str = "localhost", protocol: str = "tcp", push_port: int = 28281, pull_port: int = 28282,
                 response_timeout: int = 10, response_poll_delay: int = 0.1, socket_poll_timeout: int = 1000,
                 verbose: bool = False):
        """
        :param host:                    The hostname or IP address of the server running the MetaTrader terminal.
        :param protocol:                The socket protocol.
        :param push_port:               The PUSH port.  Must match the bridge's PULL port.
        :param pull_port:               The PULL port.  Must match the bridge's PUSH port.
        :param response_timeout:        The number of seconds to wait for a response after a request is made.
        :param response_poll_delay:     The response polling interval in seconds.
        :param socket_poll_timeout:     The socket polling timeout in milliseconds.
        :param verbose:                 Whether to print trace messages.
        """
        # the most recently PULL'd server response
        self._latest_response = None

        self._is_running = True
        self._poll_timeout = socket_poll_timeout
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
        """Get an interface for querying account details."""
        resp = self._get_response(request={"action": "GET_ACCOUNT_INFO"},
                                  timeout_message="Failed to fetch account")
        return Account(mt4=self, **resp)

    def symbols(self) -> List[str]:
        """Get the list of market symbols supported by the broker."""
        return self._get_response(request={"action": "GET_SYMBOLS"},
                                  timeout_message="Failed to fetch market symbols",
                                  default=[])

    def symbol(self, symbol: str) -> Symbol:
        """Get an interface for querying about a market symbol."""
        resp = self._get_response(request={
            "action": "GET_SYMBOL_INFO",
            "symbol": symbol
        }, timeout_message=f"Failed to fetch symbol: '{symbol}'")
        return Symbol(mt4=self, **resp)

    def signals(self) -> Dict[str, Signal]:
        """Get all trading signals from the MT4 terminal."""
        resp = self._get_response(request={"action": "GET_SIGNALS"},
                                  timeout_message="Failed to get trading signals",
                                  default={})
        return {key: Signal(**value) for key, value in resp.items()}

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

    def _get_response(self, request: Dict[str, Any], timeout_message: str = "Timed out.", default: Any = None) -> Any:
        """
        Sends a request object to the server and waits for a response.

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
        warning_message = "\n".join(resp["warnings"]) if "warnings" in resp else resp.get("warning")
        if warning_message is not None:
            print(str(warning_message))

        # unwrap the response
        return resp.get("response", default)

    def _send_object(self, message: Dict[str, Any]):
        """
        Sends a request object to the server, serialized as JSON.

        :param message: The request to send MetaTrader.  Must have an `action` property.
        """
        if self._push_socket.poll(self._poll_timeout, zmq.POLLOUT):
            try:
                self._push_socket.send_json(message, zmq.DONTWAIT)
                self._print_trace(f"Request:  {message}")
            except zmq.ZMQError as e:
                self._print_exception(e)

    def _poll_for_responses(self):
        """Background task.  Polls the pull-socket for JSON responses sent by MetaTrader."""
        while self._is_running:
            if self._pull_socket.poll(self._poll_timeout, zmq.POLLIN):
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
