from time import time, sleep
from typing import Dict, Any
from mt4_client_connector import MetaTrader4ClientConnector


class MetaTrader4Api:
    """A client interface for a remote MetaTrader 4 terminal."""

    def __init__(self, response_timeout: int = 10, **zeromq_config):
        """
        :param response_timeout:    The number of seconds to wait for a response after a request is made.
        :param zeromq_config:       The MetaTrader-ZeroMQ connection params.
        """
        self._response_poll_delay = 0.1
        self._response_timeout = response_timeout
        self._zmq = MetaTrader4ClientConnector(**zeromq_config)

    def shutdown(self):
        """Closes the ZeroMQ connection to the MetaTrader terminal"""
        self._zmq.shutdown()

    def get_response(self, request: Dict[str, Any], timeout_message: str = "Timed out.", default: Any = None) -> Any:
        """
        Sends a request object to the server and waits for a response.

        :param request:         The request to send.  Must have an `action` property.
        :param timeout_message: The message to raise if response times out.
        :param default:         The default return value.
        :return:                The server response or the default value if response is empty.
        """
        self._zmq.latest_response = None
        self._zmq.send_object(request)

        # poll for response
        start = time()
        while self._zmq.latest_response is None:
            sleep(self._response_poll_delay)
            if (time() - start) > self._response_timeout:
                break
        if self._zmq.latest_response is None:
            raise TimeoutError(timeout_message)

        # raise any errors
        resp = self._zmq.latest_response
        error_code = resp.get("error_code")
        error_message = "\n".join(resp["errors"]) if "errors" in resp else resp.get("error")
        if error_code is not None or error_message is not None:
            raise Exception(f"[{error_code}] {error_message}")

        # print any warnings to STDOUT
        warning_message = "\n".join(resp["warnings"]) if "warnings" in resp else resp.get("warning")
        if warning_message is not None:
            print(str(warning_message))

        # unwrap the response
        return resp.get("response", default)
