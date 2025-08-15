import sys
import map.map as generate_map
import units.units as unit_handler
import players.player_handler as player_handler
import config as config
import generator.map_generator_config as map_generator_config
import generator.unit_generator_config as unit_generator_config
from Agents.actions import CompleteUnitAction
from Agents.actions import UnitAction
from generator.unit_generator import UnitGenerator
import gamestate as gamestate
import utils

import random

WIDTH, HEIGHT = config.map_settings["pixel_width"], config.map_settings["pixel_height"]
ROWS, COLUMNS = config.map_settings["tile_height"], config.map_settings["tile_width"]

class MLEnv:
    def __init__(self):
        self.map = generate_map.HexMap(ROWS, COLUMNS)
        self.units = unit_handler.UnitHandler(None)
        self.players = player_handler.PlayerHandler()
        self.game_state = gamestate.GameState(self.players, self.units, self.map)
        self.players.game_state = self.game_state
        self.units.game_state = self.game_state
        self.current_player_id = 0

        self.create_env()
    
    def create_env(self):
        self.num_players = random.randint(config.min_players, config.max_players)
        config.num_players = self.num_players
        while config.num_players != len(self.game_state.players.players):
            if config.num_players < len(self.game_state.players.players):
                self.game_state.players.remove_player()
            else:
                self.game_state.players.add_player()
        self.randomize_map()
        self.randomize_units()
        self.game_state.players.start_game("AIvAI")

    def randomize_map(self):
        # Randomize config variables
        for config_key in map_generator_config.MapConfig.keys():
            if config_key != 'seed':
                map_generator_config.MapConfig[config_key]["current"] = random.randint(map_generator_config.MapConfig[config_key]["min_val"], map_generator_config.MapConfig[config_key]["max_val"])
        self.map.randomize_map()

    def randomize_units(self):
        for i, player in enumerate(unit_generator_config.PlayerUnits):
            if i >= self.num_players:
                unit_generator_config.PlayerUnits[player]["Melee"] = 0
                unit_generator_config.PlayerUnits[player]["Ranged"] = 0
                unit_generator_config.PlayerUnits[player]["Cavalry"] = 0
            else:
                unit_generator_config.PlayerUnits[player]["Melee"] = random.randint(unit_generator_config.UnitSliderConfig["Melee"]["min_val"], unit_generator_config.UnitSliderConfig["Melee"]["max_val"])
                unit_generator_config.PlayerUnits[player]["Ranged"] = random.randint(unit_generator_config.UnitSliderConfig["Ranged"]["min_val"], unit_generator_config.UnitSliderConfig["Ranged"]["max_val"])
                unit_generator_config.PlayerUnits[player]["Cavalry"] = random.randint(unit_generator_config.UnitSliderConfig["Cavalry"]["min_val"], unit_generator_config.UnitSliderConfig["Cavalry"]["max_val"])
                if unit_generator_config.PlayerUnits[player]["Melee"] + unit_generator_config.PlayerUnits[player]["Ranged"] + unit_generator_config.PlayerUnits[player]["Cavalry"] == 0:
                    unit_generator_config.PlayerUnits[player]["Melee"] = 1
        unit_generator = UnitGenerator(self.game_state)
        unit_generator.generate_units()

    def next_action(self, action):
        action_dict = {
            0: "Move",
            1: "Swap",
            2: "Attack",
            3: "Fortify"
        }
        axial_origin = utils.coord_to_hex_coord(action["coord_y"], action["coord_x"])
        origin_tile = self.game_state.map.get_tile_hex(*axial_origin)
        origin_unit = self.game_state.units.get_unit(origin_tile.unit_id)
        axial_destination = utils.coord_to_hex_coord(action["target_y"], action["target_x"])
        best_action = UnitAction(action_dict[action["action_type"]], origin_unit, self.game_state, axial_destination, find_score=False)
        if best_action.type == "Move" or best_action.type == "Swap":
            CompleteUnitAction.move_unit(best_action.unit, best_action.target)
        elif best_action.type == "Attack":
            CompleteUnitAction.attack(best_action.unit, best_action.target)
        elif best_action.type == "Fortify":
            CompleteUnitAction.fortify(best_action.unit)
            
    def next_turn(self):
        current_player = self.game_state.players.get_player(self.current_player_id)

        for unit_id in current_player.units:
            self.game_state.units.get_unit(unit_id).end_turn()
        current_player.update_visibility()
        if self.current_player_id >= len(self.game_state.players.players) - 1:
            self.current_player_id = 0
        else:
            self.current_player_id += 1
        current_player = self.game_state.players.get_player(self.current_player_id)
        while current_player.eliminated:
            if self.current_player_id >= len(self.game_state.players.players) - 1:
                self.current_player_id = 0
            else:
                self.current_player_id += 1
            current_player = self.game_state.players.get_player(self.current_player_id)
        for unit in current_player.units:
            self.game_state.units.get_unit(unit).turn_begin()
        current_player.update_visibility()

        self.interfaces.player_v_AI_test_interface.update_UI(self.current_player_id)

    def game_win(self):
        num_players = len(self.game_state.players.players)
        num_alive = 0
        for player_id in range(num_players):
            current_player = self.game_state.players.get_player(player_id)
            if len(current_player.elim_units) >= len(current_player.units):
                current_player.eliminated = True
            if current_player.eliminated == False:
                num_alive += 1
        if num_alive <= 1:
            return True
        return False

