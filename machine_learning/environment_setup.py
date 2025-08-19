import sys
import map.map as generate_map
import units.units as unit_handler
import players.player_handler as player_handler
import config as config
import machine_learning.ml_config as ml_config
import generator.map_generator_config as map_generator_config
import generator.unit_generator_config as unit_generator_config
from Agents.actions import CompleteUnitAction
from Agents.actions import UnitAction
from Agents.actions import Actions

from generator.unit_generator import UnitGenerator
import gamestate as gamestate
import utils

import random

from logs.logging import Logging

WIDTH, HEIGHT = config.map_settings["pixel_width"], config.map_settings["pixel_height"]
ROWS, COLUMNS = config.map_settings["tile_height"], config.map_settings["tile_width"]

class MLEnv:
    def __init__(self):
        self.game_state = gamestate.GameState()
        self.current_player_id = 0

        self.total_friendly_units = 0
        self.total_enemy_units = 0

        self.AI_kill_enemy_score = 0
        self.AI_kill_friendly_score = 0
        self.AI_win_score = 0

        self.winner = -1

        self.player_stats = []

        self.create_env()
    
    def create_env(self):
        self.num_players = 2 #random.randint(config.min_players, config.max_players)
        config.num_players = self.num_players
        config.game_type == "AIvAI"
        while config.num_players != len(self.game_state.players.players):
            if config.num_players < len(self.game_state.players.players):
                self.game_state.players.remove_player()
            else:
                self.game_state.players.add_player()
        print("Num Players:", config.num_players)
        self.randomize_map()
        print("Map Generated")
        self.randomize_units(False)
        print("Units Randomized")
        self.allocate_scores()
        self.game_state.start()
        Logging.log_game_init(self.game_state)


    def randomize_map(self):
        # Randomize config variables
        for config_key in map_generator_config.MapConfig.keys():
            if config_key != 'seed':
                map_generator_config.MapConfig[config_key]["current"] = random.randint(map_generator_config.MapConfig[config_key]["min_val"], map_generator_config.MapConfig[config_key]["max_val"])
        self.game_state.map.randomize_map()

    def randomize_units(self, random = True):
        if random:
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
                    print("Player", i, "units: ")
                    print("Melee:",unit_generator_config.PlayerUnits[player]["Melee"])
                    print("Ranged:",unit_generator_config.PlayerUnits[player]["Ranged"])
                    print("Cavalry:",unit_generator_config.PlayerUnits[player]["Cavalry"])
                    stats_dict = {
                        "Kills": 0,
                        "Deaths": 0,
                        "Melee": unit_generator_config.PlayerUnits[player]["Melee"],
                        "Ranged": unit_generator_config.PlayerUnits[player]["Ranged"],
                        "Cavalry": unit_generator_config.PlayerUnits[player]["Cavalry"],
                        "Move": 0,
                        "Attack": 0,
                        "Fortify": 0,
                        "Score": 0
                    }
                    self.player_stats.append(stats_dict.copy())
                if i == 0:
                    self.total_friendly_units += unit_generator_config.PlayerUnits[player]["Melee"] + unit_generator_config.PlayerUnits[player]["Ranged"] + unit_generator_config.PlayerUnits[player]["Cavalry"]
                else:
                    self.total_enemy_units += unit_generator_config.PlayerUnits[player]["Melee"] + unit_generator_config.PlayerUnits[player]["Ranged"] + unit_generator_config.PlayerUnits[player]["Cavalry"]
        else:
            for i, player in enumerate(unit_generator_config.PlayerUnits):
                if i >= self.num_players:
                    unit_generator_config.PlayerUnits[player]["Melee"] = 0
                    unit_generator_config.PlayerUnits[player]["Ranged"] = 0
                    unit_generator_config.PlayerUnits[player]["Cavalry"] = 0
                else:
                    unit_generator_config.PlayerUnits[player]["Melee"] = 2
                    unit_generator_config.PlayerUnits[player]["Ranged"] = 2
                    unit_generator_config.PlayerUnits[player]["Cavalry"] = 2
                    print("Player", i, "units: ")
                    print("Melee:",unit_generator_config.PlayerUnits[player]["Melee"])
                    print("Ranged:",unit_generator_config.PlayerUnits[player]["Ranged"])
                    print("Cavalry:",unit_generator_config.PlayerUnits[player]["Cavalry"])
                    stats_dict = {
                        "Kills": 0,
                        "Deaths": 0,
                        "Melee": unit_generator_config.PlayerUnits[player]["Melee"],
                        "Ranged": unit_generator_config.PlayerUnits[player]["Ranged"],
                        "Cavalry": unit_generator_config.PlayerUnits[player]["Cavalry"],
                        "Move": 0,
                        "Attack": 0,
                        "Fortify": 0,
                        "Score": 0
                    }
                    self.player_stats.append(stats_dict.copy())
                if i == 0:
                    self.total_friendly_units += unit_generator_config.PlayerUnits[player]["Melee"] + unit_generator_config.PlayerUnits[player]["Ranged"] + unit_generator_config.PlayerUnits[player]["Cavalry"]
                else:
                    self.total_enemy_units += unit_generator_config.PlayerUnits[player]["Melee"] + unit_generator_config.PlayerUnits[player]["Ranged"] + unit_generator_config.PlayerUnits[player]["Cavalry"]

        unit_generator = UnitGenerator(self.game_state)
        unit_generator.generate_units()

    def allocate_scores(self):
        self.AI_kill_enemy_score = ml_config.KILL_SCORE_TOTAL / self.total_enemy_units
        self.AI_kill_friendly_score = ml_config.DEATH_SCORE_TOTAL / self.total_friendly_units
        self.AI_win_score = ml_config.WIN_TOTAL


    def score_choose_best_action(self):
        legal_actions = Actions.get_actions(self.current_player_id, self.game_state)
        if legal_actions == []:
            return (False, 0, 0, 0)
        best_action = None
        for action in legal_actions:
            if best_action == None or action.score > best_action.score:
                best_action = action
        # To handle scenario where unit paths to farther location but due to terrain, still has remaining movement. Want to do a double check if they really want to move there.
        if best_action.unit.AI_last_move == (best_action.type, best_action.target):
            best_action.unit.AI_action = False
        else:
            best_action.unit.AI_last_move = (best_action.type, best_action.target)
        origin_unit = best_action.unit
        score = 0
        destination_unit_id = None
        if best_action.type == "Move" or best_action.type == "Swap":
            print(f"Action: Move - Unit {best_action.unit.id} at {best_action.unit.coord} moves to {best_action.target}")
            CompleteUnitAction.move_unit(best_action.unit, best_action.target)
            self.player_stats[self.current_player_id]["Move"] += 1

        elif best_action.type == "Attack":
            destination_tile = self.game_state.map.get_tile_hex(*best_action.target)
            destination_unit = self.game_state.units.get_unit(destination_tile.unit_id)
            print(f"Action: Attack - Unit {best_action.unit.id} at {best_action.unit.coord} attacks unit at {best_action.target}")
            CompleteUnitAction.attack(best_action.unit, best_action.target)
            if self.current_player_id == 0:
                if destination_unit.alive == False:
                    score = self.AI_kill_enemy_score

                elif origin_unit.alive == False:
                    score = self.AI_kill_friendly_score

            elif destination_unit.owner_id == 0:
                if destination_unit.alive == False:
                    score = self.AI_kill_friendly_score
                elif origin_unit.alive == False:
                    score = self.AI_kill_enemy_score


            if destination_unit.alive == False:
                self.player_stats[self.current_player_id]["Kills"] += 1
                self.player_stats[destination_unit.owner_id]["Deaths"] += 1
                self.player_stats[self.current_player_id]["Score"] += self.AI_kill_enemy_score
                self.player_stats[destination_unit.owner_id]["Score"] += self.AI_kill_friendly_score
            elif origin_unit.alive == False:
                self.player_stats[self.current_player_id]["Deaths"] += 1
                self.player_stats[destination_unit.owner_id]["Kills"] += 1
                self.player_stats[self.current_player_id]["Score"] += self.AI_kill_friendly_score
                self.player_stats[destination_unit.owner_id]["Score"] += self.AI_kill_enemy_score
            destination_unit_id = destination_unit.id
            self.player_stats[self.current_player_id]["Attack"] += 1
        elif best_action.type == "Fortify":
            print(f"Action: Fortify - Unit {best_action.unit.id} at {best_action.unit.coord} fortifies")
            CompleteUnitAction.fortify(best_action.unit)
            self.player_stats[self.current_player_id]["Fortify"] += 1

        return (True, score, origin_unit.id, destination_unit_id)

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
        score = 0
        destination_unit_id = None
        if best_action.type == "Move" or best_action.type == "Swap":
            print(f"Action: Move - Unit {origin_tile.unit_id} at {axial_origin} moves to {axial_destination}")
            CompleteUnitAction.move_unit(best_action.unit, best_action.target)
            self.player_stats[self.current_player_id]["Move"] += 1
        elif best_action.type == "Attack":
            destination_tile = self.game_state.map.get_tile_hex(*axial_destination)
            destination_unit = self.game_state.units.get_unit(destination_tile.unit_id)
            print(f"Action: Attack - Unit {origin_tile.unit_id} at {axial_origin} attacks unit at {axial_destination}")
            CompleteUnitAction.attack(best_action.unit, best_action.target)
            if self.current_player_id == 0:
                if destination_unit.alive == False:
                    score = self.AI_kill_enemy_score

                elif origin_unit.alive == False:
                    score = self.AI_kill_friendly_score

            elif destination_unit.owner_id == 0:
                if destination_unit.alive == False:
                    score = self.AI_kill_friendly_score
                elif origin_unit.alive == False:
                    score = self.AI_kill_enemy_score


            if destination_unit.alive == False:
                self.player_stats[self.current_player_id]["Kills"] += 1
                self.player_stats[destination_unit.owner_id]["Deaths"] += 1
                self.player_stats[self.current_player_id]["Score"] += self.AI_kill_enemy_score
                self.player_stats[destination_unit.owner_id]["Score"] += self.AI_kill_friendly_score
            elif origin_unit.alive == False:
                self.player_stats[self.current_player_id]["Deaths"] += 1
                self.player_stats[destination_unit.owner_id]["Kills"] += 1
                self.player_stats[self.current_player_id]["Score"] += self.AI_kill_friendly_score
                self.player_stats[destination_unit.owner_id]["Score"] += self.AI_kill_enemy_score
            destination_unit_id = destination_unit.id
            self.player_stats[self.current_player_id]["Attack"] += 1

        elif best_action.type == "Fortify":
            print(f"Action: Fortify - Unit {origin_tile.unit_id} at {axial_origin} fortifies")
            CompleteUnitAction.fortify(best_action.unit)
            self.player_stats[self.current_player_id]["Fortify"] += 1


        return (score, origin_unit.id, destination_unit_id)
            

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
            for player_id in range(num_players):
                current_player = self.game_state.players.get_player(player_id)
                if current_player.eliminated == False:
                    self.winner = player_id
                    self.player_stats[player_id]["Score"] += self.AI_win_score
                    self.game_state.winner = player_id 
                    break
            return True
        return False

