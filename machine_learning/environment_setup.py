import sys
import map.map as generate_map
import units.units as unit_handler
import players.player_handler as player_handler
import config as config
import generator.map_generator_config as map_generator_config
import generator.unit_generator_config as unit_generator_config
from Agents.actions import CompleteUnitAction
from generator.unit_generator import UnitGenerator
import gamestate as gamestate

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
                print(config_key)
                map_generator_config.MapConfig[config_key]["current"] = random.randint(map_generator_config.MapConfig[config_key]["min_val"], map_generator_config.MapConfig[config_key]["max_val"])
        self.map.randomize_map()

    def randomize_units(self):
        for i, player in enumerate(unit_generator_config.PlayerUnits):
            print(player)
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

    def next_action(best_action):
        if best_action.type == "Move" or best_action.type == "Swap":
            CompleteUnitAction.move_unit(best_action.unit, best_action.target)
        elif best_action.type == "Attack":
            CompleteUnitAction.attack(best_action.unit, best_action.target)
        elif best_action.type == "Fortify":
            CompleteUnitAction.fortify(best_action.unit)

    def game_win(self):
        pass
