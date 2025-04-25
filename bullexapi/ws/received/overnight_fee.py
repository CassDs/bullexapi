"""Module for Bullex websocket."""

def overnight_fee(api, message):
    if message["name"] == "overnight-fee":
        api.overnight_fee = message