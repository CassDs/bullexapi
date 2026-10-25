"""Module for Bullex websocket."""


def training_balance_reset(api, message):
    if message["name"] == "training-balance-reset":
        msg = message.get("msg")
        if isinstance(msg, dict) and "isSuccessful" in msg:
            api.training_balance_reset_request = msg["isSuccessful"]
        else:
            api.training_balance_reset_request = (message.get("status") == 2000)
