"""Module for websocket candles_generated v2."""
import bullexapi.constants as OP_code


def candle_generated_v2(api, message, dict_queue_add):
    if message["name"] == "candles-generated":
        active_id = message["msg"]["active_id"]
        matching_names = [k for k, v in OP_code.ACTIVES.items() if v == active_id]
        if not matching_names:
            return
        for active in matching_names:
            active_str = str(active)
            for k, v in message["msg"]["candles"].items():
                v["active_id"] = active_id
                v["at"] = message["msg"]["at"]
                v["ask"] = message["msg"]["ask"]
                v["bid"] = message["msg"]["bid"]
                v["close"] = message["msg"]["value"]
                v["size"] = int(k)
                size = int(v["size"])
                from_ = int(v["from"])
                maxdict = api.real_time_candles_maxdict_table[active_str][size]
                if not isinstance(maxdict, int):
                    maxdict = 10
                dict_queue_add(api.real_time_candles, maxdict, active_str, size, from_, v)
            api.candle_generated_all_size_check[active_str] = True
