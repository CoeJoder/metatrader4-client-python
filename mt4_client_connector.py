import zmq

from typing import Any, Dict
from time import sleep
from threading import Thread


class MetaTrader4ClientConnector:
    """Client interface for a MetaTrader bridge.  The connection is established using reciprocal
    PUSH/PULL ZeroMQ sockets."""

    def __init__(self, host: str = "localhost", protocol: str = "tcp", push_port: int = 28281, pull_port: int = 28282,
                 socket_poll_timeout: int = 1000, socket_poll_interval: int = 1, verbose: bool = False):
        """
        :param host:                    The hostname or IP address of the server running the MetaTrader terminal.
        :param protocol:                The socket protocol.
        :param push_port:               The PUSH port.  Must match the bridge's PULL port.
        :param pull_port:               The PULL port.  Must match the bridge's PUSH port.
        :param socket_poll_timeout:     The socket polling timeout in milliseconds.
        :param socket_poll_interval:    The socket polling interval in milliseconds.
        :param verbose:                 Whether to print trace messages.
        """
        self.latest_response = None
        """The most recently PULL'd server response."""

        self._is_running = True
        self._poll_timeout = socket_poll_timeout
        self._sleep_delay = float(socket_poll_interval) * 1000.0
        self._verbose = verbose

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

    def send_object(self, message: Dict[str, Any]):
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
            sleep(self._sleep_delay)
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
