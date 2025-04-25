"""Module for Bullex websocket."""

def sold_options(api, message):
    if message["name"] == "sold-options":
        api.sold_options_respond = message