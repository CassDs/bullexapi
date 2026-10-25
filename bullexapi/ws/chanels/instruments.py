"""Module for Bullex instruments websocket chanel."""

from bullexapi.ws.chanels.base import Base


class Get_instruments(Base):
    """Class for Bullex instruments websocket chanel."""
    # pylint: disable=too-few-public-methods

    name = "sendMessage"

    def __call__(self, types):
        t = str(types).lower()
        if t in ("forex", "cfd", "crypto"):
            data = {
                "name": f"marginal-{t}-instruments.get-underlying-list",
                "version": "1.0",
                "body": {},
            }
        else:
            data = {
                "name": "get-instruments",
                "version": "4.0",
                "body": {"type": types},
            }

        self.send_websocket_request(self.name, data)
