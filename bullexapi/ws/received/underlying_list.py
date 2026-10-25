"""Module for Bullex websocket."""


def underlying_list(api, message):
    if message["name"] == "underlying-list":
        msg = message.get("msg", {})
        if isinstance(msg, dict) and "items" in msg:
            items = msg["items"]
            for item in items:
                if "id" not in item and "name" in item:
                    item["id"] = item["name"]
            api.instruments = {"instruments": items}
        else:
            api.underlying_list_data = msg
