import zmq

from time import time, sleep
from typing import Any, Dict
from time import sleep
from threading import Thread
from errors import MT4Error


class MetaTrader4ClientConnector:
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
        self.latest_response = None

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

    def get_response(self, request: Dict[str, Any], timeout_message: str = "Timed out.", default: Any = None) -> Any:
        """
        Sends a request object to the server and waits for a response.

        :param request:         The request to send.  Must have an `action` property.
        :param timeout_message: The message to raise if response times out.
        :param default:         The default return value.
        :return:                The server response or the default value if response is empty.
        """
        self.latest_response = None
        self._send_object(request)

        # poll for response
        start = time()
        while self.latest_response is None:
            sleep(self._response_poll_delay)
            if (time() - start) > self._response_timeout:
                break
        if self.latest_response is None:
            raise TimeoutError(timeout_message)

        # raise any errors
        resp = self.latest_response
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
                        self.latest_response = response
                except zmq.ZMQError as e:
                    self._print_exception(e)

    def _print_trace(self, message: str):
        if self._verbose:
            print(f"[MT4-ZMQ] {message}")

    @staticmethod
    def _print_exception(ex: Exception):
        print(f"[MT4-ZMQ ERROR] {ex}")
