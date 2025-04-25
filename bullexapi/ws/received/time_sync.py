"""Module for Bullex websocket."""

def time_sync(api, message):
    if message["name"] == "timeSync":
        api.timesync.server_timestamp = message["msg"]