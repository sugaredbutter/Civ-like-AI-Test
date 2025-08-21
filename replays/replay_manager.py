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
        self.current_turn_index = 0
        self.current_player = 0
        self.current_action_index = 0
        self.num_turns = 0
    
    def setup(self, log_num):
        self.data = None
        self.current_turn_index = 0
        self.current_player = 0
        self.current_action_index = 0
        self.num_turns = 0
        folder = os.path.join(os.path.dirname(__file__), "..", "logs", "game_logs")  
        if not os.path.exists(folder):
            return False
        log_file = os.path.join(folder, f"game_log_{log_num}.json")
        if not os.path.exists(log_file):
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
        self.num_turns = len(self.data["turns"])
        config.game_type = "AIvAI"

        self.game_state.start()

    def complete_next_action(self):
        next_action = self.find_next_action()
        if next_action == None:
            return False
        unit = self.game_state.units.get_unit(next_action["ID"])
        if next_action["Type"] == "Move":
            unit.move_to(ast.literal_eval(next_action["Destination"]))
        elif next_action["Type"] == "Attack":
            unit.attack_enemy(ast.literal_eval(next_action["Destination"]), (next_action["DMG_Inflicted"], next_action["DMG_Taken"]))
        elif next_action["Type"] == "Fortify":
            unit.fortify()
        elif next_action["Type"] == "Heal":
            unit.heal()
        elif next_action["Type"] == "Skip":
            unit.skip_turn()
        elif next_action["Type"] == "Cancel":
            unit.cancel_action()
        return True
    
    def begin_turn(self, current_player):
        for unit in current_player.units:
            self.game_state.units.get_unit(unit).turn_begin()
        current_player.update_visibility()


    def end_turn(self, current_player):
        for unit_id in current_player.units:
            self.game_state.units.get_unit(unit_id).end_turn()
        current_player.update_visibility()




    def find_next_action(self):
        next_action = None
        while self.current_turn_index < self.num_turns:
            current_turn = self.data["turns"][self.current_turn_index]
            current_player_actions = current_turn.get(str(self.current_player), None)
            if current_player_actions == None or self.current_action_index >= len(current_player_actions):
                current_player = self.game_state.players.get_player(self.current_player)
                self.end_turn(current_player)
                turn = self.get_next_player()
                if turn:
                    self.current_turn_index += 1
                current_player = self.game_state.players.get_player(self.current_player)
                self.begin_turn(current_player)
                self.current_action_index = 0
                
            else:
                next_action = current_player_actions[self.current_action_index]
                self.current_action_index += 1
                return next_action
        self.check_win()
        return next_action

            
    def get_next_player(self):
        turn = False
        if self.current_player >= len(self.game_state.players.players) - 1:
            self.current_player = 0
            turn = True
        else:
            self.current_player += 1
        current_player = self.game_state.players.get_player(self.current_player)
        while current_player.eliminated:
            if self.current_player >= len(self.game_state.players.players) - 1:
                self.current_player = 0
                turn = True
            else:
                self.current_player += 1
            current_player = self.game_state.players.get_player(self.current_player)

        return turn
    
    def check_win(self):
        num_players = len(self.game_state.players.players)
        num_alive = 0
        for player_id in range(num_players):
            current_player = self.game_state.players.get_player(player_id)
            if len(current_player.elim_units) >= len(current_player.units):
                current_player.eliminated = True
            if current_player.eliminated == False:
                num_alive += 1
        if num_alive <= 1:
            for player_id in range(num_players):
                current_player = self.game_state.players.get_player(player_id)
                if current_player.eliminated == False:
                    self.game_state.winner = player_id 
