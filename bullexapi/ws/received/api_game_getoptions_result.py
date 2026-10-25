"""Module for Bullex websocket."""


def api_game_getoptions_result(api, message):
    if message["name"] == "api_game_getoptions_result":
        api.api_game_getoptions_result = message
    elif message["name"] == "options":
        api.get_options_v2_data = message
