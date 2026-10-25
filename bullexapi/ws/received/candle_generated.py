"""Module for websocket candle_generated."""
import bullexapi.constants as OP_code


def candle_generated_realtime(api, message, dict_queue_add):
    if message["name"] == "candle-generated":
        active_id = message["msg"]["active_id"]
        matching_names = [k for k, v in OP_code.ACTIVES.items() if v == active_id]
        if not matching_names:
            return
        size = int(message["msg"]["size"])
        from_ = int(message["msg"]["from"])
        msg = message["msg"]
        for active in matching_names:
            active_str = str(active)
            maxdict = api.real_time_candles_maxdict_table[active_str][size]
            if not isinstance(maxdict, int):
                maxdict = 10
            dict_queue_add(api.real_time_candles, maxdict, active_str, size, from_, msg)
            api.candle_generated_check[active_str][size] = True
