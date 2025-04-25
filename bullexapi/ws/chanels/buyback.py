"""Module for Bullex buyback websocket chanel."""

from bullexapi.ws.chanels.base import Base


class Buyback(Base):
    """Class for Bullex subscribe to buyback websocket chanel."""
    # pylint: disable=too-few-public-methods

    name = "buyback"

    def __call__(self):
        """Method to send message to buyback websocket chanel."""
        pass
