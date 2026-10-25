"""Module for bullex buy blitz option websocket chanel."""
import time
import bullexapi.global_value as global_value
from bullexapi.ws.chanels.base import Base
from random import randint


class BuyBlitzOption(Base):
    """Class for bullex blitz option websocket chanel."""
    # pylint: disable=too-few-public-methods

    name = "sendMessage"

    def __call__(self, price, active_id, direction, expiration_size, profit_percent, value=None, request_id=None):
        if request_id is None:
            request_id = str(randint(0, 10000))

        server_ts = int(self.api.timesync.server_timestamp) if getattr(self.api.timesync, "server_timestamp", None) else int(time.time())
        expired = server_ts + int(expiration_size)

        data = {
            "name": "binary-options.open-option",
            "version": "2.0",
            "body": {
                "user_balance_id": int(global_value.balance_id),
                "active_id": int(active_id),
                "option_type_id": 12,  # 12 is for blitz option
                "direction": direction.lower(),
                "expired": expired,
                "refund_value": 0,
                "price": float(price),
                "profit_percent": int(profit_percent),
                "expiration_size": int(expiration_size),
            },
        }

        if value is not None:
            data["body"]["value"] = value

        self.send_websocket_request(self.name, data, request_id)
        return request_id
