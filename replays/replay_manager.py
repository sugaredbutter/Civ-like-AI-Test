import os
import config
from pathlib import Path
import json
import ast
import map.map as current_map
import units.units as units

class ReplayManager:
    def __init__(self, game_state):
        self.game_state = game_state
        self.data = None
        self.current_turn = 1
    
    def setup(self, log_num):
        self.current_turn = 1
        self.data = None
        folder = os.path.join(os.path.dirname(__file__), "..", "logs", "game_logs")  
        file_name = f"game_log_{log_num}.json"
        if not os.path.exists(folder):
            print("1")
            return False
        log_file = os.path.join(folder, f"game_log_{log_num}.json")
        if not os.path.exists(log_file):
            print("2")
            return False
        with open(log_file, "r") as f:
            self.data = json.load(f)

        self.num_players = self.data["num_players"]
        while self.num_players != len(self.game_state.players.players):
            if self.num_players < len(self.game_state.players.players):
                self.game_state.players.remove_player()
            else:
                self.game_state.players.add_player()

        new_map = {}
        map_info = self.data["map"]
        for tile_coord in map_info.keys():
            tile_info = map_info[tile_coord]
            tuple_tile_coord = ast.literal_eval(tile_coord)
            tile = current_map.Tile(*tuple_tile_coord, tile_info["biome"], tile_info["terrain"], tile_info["feature"], tile_info["rivers"])
            new_map[tuple_tile_coord] = tile


        new_units = {}
        units_info = self.data["units"]
        for unit_id in units_info.keys():
            unit_info = units_info[unit_id]
            int_unit_id = int(unit_id)
            tuple_unit_coord = ast.literal_eval(unit_info["coord"])
            new_units[int_unit_id] = units.Unit(unit_info["owner_id"], int_unit_id, unit_info["type"], unit_info["health"], tuple_unit_coord, None, self.game_state)
            player = self.game_state.players.get_player(unit_info["owner_id"])
            player.units.append(int_unit_id)
            new_map[tuple_unit_coord].unit_id = int_unit_id

        self.game_state.map.tiles = new_map
        self.game_state.units.units = new_units

    def next_action():
        
        pass
