import os
import config
from pathlib import Path
import json
class LoggingML:
    def log_ML_stats(info, sys_stats = None):
        folder = os.path.join(os.path.dirname(__file__), "ml_logs")  
        if not os.path.exists(folder):
            os.makedirs(folder)
        if config.ML_log_file == -1:
            # Find existing logs
            existing = [f for f in os.listdir(folder) if f.startswith("training_log_") and f.endswith(".txt")]
            nums = []
            for f in existing:
                try:
                    n = int(f.replace("training_log_", "").replace(".txt", ""))
                    nums.append(n)
                except ValueError:
                    pass

            next_num = max(nums) + 1 if nums else 1
            log_file = os.path.join(folder, f"training_log_{next_num}.txt")
            config.ML_log_file = next_num
        else:
            log_file = os.path.join(folder, f"training_log_{config.ML_log_file}.txt")


        # Append new log entry
        with open(log_file, "a") as f:
            f.write("=====================================================================\n")
            f.write(f"Game: {info["Game"]} - Turns: {info["Turns"]}\n")
            f.write(f"Game ID: {info["Game_id"]}\n")
            f.write(f"Winner: {info["Winner"]}\n")
            for player in range(info["Num_Players"]):
                f.write(f"Player {player} - Model: {'Latest' if player == 0 else info['Models'][player] if info['Models'][player] is not None else 'Score-based'}\n")
                f.write(f"Score: {info["Players"][player]["Score"]}\n")
                f.write(f"Melee: {info["Players"][player]["Melee"]}\n")
                f.write(f"Ranged: {info["Players"][player]["Ranged"]}\n")
                f.write(f"Cavalry: {info["Players"][player]["Cavalry"]}\n")
                f.write(f"Kills: {info["Players"][player]["Kills"]}\n")
                f.write(f"Deaths: {info["Players"][player]["Deaths"]}\n")
                f.write(f"Move: {info["Players"][player]["Move"]}\n")
                f.write(f"Attack: {info["Players"][player]["Attack"]}\n")
                f.write(f"Fortify: {info["Players"][player]["Fortify"]}\n\n")

            f.write(f"AI score: {info["AI_score"]}\n")
            f.write(f"Loss: {info["Loss"]}\n")

            if sys_stats != None:
                for k, v in sys_stats.items():
                    f.write(f"{k}: {v}\n")

class Logging:
    def log_game_init(game_state):
        folder = os.path.join(os.path.dirname(__file__), "game_logs")  
        if not os.path.exists(folder):
            os.makedirs(folder)
    
        # Find existing logs
        existing = [f for f in os.listdir(folder) if f.startswith("game_log_") and f.endswith(".json")]
        nums = []
        for f in existing:
            try:
                n = int(f.replace("game_log_", "").replace(".json", ""))
                nums.append(n)
            except ValueError:
                pass

        next_num = max(nums) + 1 if nums else 1
        log_file = os.path.join(folder, f"game_log_{next_num}.json")
        config.log_file = next_num
        with open(log_file, "w") as f:
            game_info = {}
            saved_map = {}
            saved_units = {}
            for tile_coord in game_state.map.tiles.keys():
                tile = game_state.map.tiles[tile_coord]
                str_tile_coord = str(tile_coord)

                saved_map[str_tile_coord] = {
                    "biome": tile.biome,
                    "terrain": tile.terrain,
                    "feature": tile.feature,
                    "rivers": tile.rivers
                }

            for unit_id in game_state.units.units.keys():
                unit = game_state.units.units[unit_id]
                saved_units[unit_id] = {
                    "owner_id": unit.owner_id,
                    "type": unit.type,
                    "health": unit.health,
                    "coord": str(unit.coord)
                }
            game_info["id"] = game_state.game_id
            game_info["num_players"] = config.num_players
            game_info["map"] = saved_map
            game_info["units"] = saved_units
            game_info["player_stats"] = {}
            for player_id in range(config.num_players):
                player = game_state.players.get_player(player_id)
                type_counter = [0, 0, 0]
                for unit_id in player.units:
                    unit = game_state.units.get_unit(unit_id)
                    if unit.type == "Melee":
                        type_counter[0] += 1
                    elif unit.type == "Ranged":
                        type_counter[1] += 1
                    elif unit.type == "Cavalry":
                        type_counter[2] += 1

                    
                player_stats = {
                    "Melee": type_counter[0],
                    "Ranged": type_counter[1],
                    "Cavalry": type_counter[2],
                    "Kills": 0,
                    "Deaths": 0,
                    "Remaining": 0
                }
                game_info["player_stats"][player_id] = player_stats

            game_info["turns"] = []
            game_info["num_turns"] = game_state.current_turn
            json.dump(game_info, f, indent=2)


    def log_action(action, game_state):
        if config.log_file == -1:
            Logging.log_game_init(game_state)
        folder = os.path.join(os.path.dirname(__file__), "game_logs")  
        log_file = os.path.join(folder, f"game_log_{config.log_file}.json")
        with open(log_file, "r") as f:
            data = json.load(f)
        data["num_turns"] = game_state.current_turn
        turn_data = data["turns"]
        while(len(turn_data) < game_state.current_turn):
            turn_data.append({})
        if turn_data[-1].get(str(game_state.current_player), None) == None:
            turn_data[-1][str(game_state.current_player)] = []
        turn_data[-1][str(game_state.current_player)].append(action)
        game_stats = data["player_stats"]
        for player_id in range(config.num_players):
            player = game_state.players.get_player(player_id)
            num_units = len(player.units)
            game_stats[str(player_id)]["Kills"] = game_state.kills[player_id]
            game_stats[str(player_id)]["Deaths"] = game_state.deaths[player_id]
            game_stats[str(player_id)]["Remaining"] = num_units - game_state.deaths[player_id]
        with open(log_file, "w") as f:
            json.dump(data, f, indent=2)

    def log_end_game_stats(game_state):
        if config.log_file == -1:
            Logging.log_game_init(game_state)
        folder = os.path.join(os.path.dirname(__file__), "game_logs")  
        log_file = os.path.join(folder, f"game_log_{config.log_file}.json")
        with open(log_file, "r") as f:
            data = json.load(f)
        data["num_turns"] = game_state.current_turn
        game_stats = data["player_stats"]
        for player_id in range(config.num_players):
            player = game_state.players.get_player(player_id)
            num_units = len(player.units)
            game_stats[str(player_id)]["Kills"] = game_state.kills[player_id]
            game_stats[str(player_id)]["Deaths"] = game_state.deaths[player_id]
            game_stats[str(player_id)]["Remaining"] = num_units - game_state.deaths[player_id]
        data["winner"] = game_state.winner
        with open(log_file, "w") as f:
            json.dump(data, f, indent=2)



            
            