"""Module for Bullex websocket."""

def heartbeat(api, message):
    if message["name"] == "heartbeat":
        try:
            api.heartbeat(message["msg"])
        except:
            pass