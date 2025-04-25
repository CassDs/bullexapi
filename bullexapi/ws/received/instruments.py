"""Module for Bullex websocket."""

def instruments(api, message):
    if message["name"] == "instruments":
            api.instruments = message["msg"]