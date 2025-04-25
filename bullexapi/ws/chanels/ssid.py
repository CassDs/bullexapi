"""Module for Bullex API ssid websocket chanel."""

from bullexapi.ws.chanels.base import Base


class Ssid(Base):
    """Class for Bullex API ssid websocket chanel."""
    # pylint: disable=too-few-public-methods

    name = "ssid"

    def __call__(self, ssid):
        """Method to send message to ssid websocket chanel.

        :param ssid: The session identifier.
        """
        self.send_websocket_request(self.name, ssid)
