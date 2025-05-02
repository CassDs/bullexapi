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
        """Method to send message to buy blitz option websocket chanel.

        :param price: The buying price.
        :param active_id: The asset ID.
        :param direction: The buying direction.
        :param expiration_size: The expiration time in seconds (typically 3, 5 or 10).
        :param profit_percent: The profit percentage offered by the broker.
        :param value: The current asset price value (optional).
        :param request_id: Custom request ID.
        """
        if request_id is None:
            request_id = str(randint(0, 10000))

        # Calculate expiration timestamp
        expired = int(time.time()) + expiration_size

        # Build data structure for the request
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
                "expiration_size": int(expiration_size)
            }
        }

        # Include asset value if provided
        if value is not None:
            data["body"]["value"] = value

        self.send_websocket_request(self.name, data, request_id)
        return request_id
