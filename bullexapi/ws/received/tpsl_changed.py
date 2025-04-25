"""Module for Bullex websocket."""

def tpsl_changed(api, message):
    if message["name"] == "tpsl-changed":
            api.tpsl_changed_respond = message