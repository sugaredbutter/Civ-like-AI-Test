import Scoring.score_config as score_config
import utils as utils
import math
from players.units_utils import UnitUtils
from players.units_utils import UnitMove
from players.units_utils import UnitVisibility
from players.units_utils import UnitAttack
from players.units_utils import UnitMoveScoring
from combat_manager.combat_manager import CombatManager


class UnitMoveScore:
    def __init__(self, unit, target_coord, game_state):
        self.game_state = game_state
        self.unit = unit
        self.target_coord = target_coord
        self.tile = self.game_state.map.get_tile_hex(*target_coord)
        self.player = game_state.players.get_player(self.unit.owner_id)
        self.score = 0
        
    def get_score(self):  #Get score
        self.exploration_score()
        self.offensive_score()
        self.defensive_score()
        self.distance_score()
        return self.score
        
    def exploration_score(self):    #Score for exploring new lands
        revealed_tiles = self.player.revealed_tiles
        if self.target_coord not in revealed_tiles:
            self.score += score_config.moveScore["unrevealed"]
        
    # Offensive Behavior
    # + Number of attackable units 
    # + Average damage + max inflicted damage on units
    # + Adjacent Enemies (for melee specifically)
    # Health Multiplier so this behavior is tuned down when lower health

    def offensive_score(self):  #Offensive/more aggressive behavior
        offensive_score = 0
        if self.unit.type != "ranged":
            attackable_enemies = UnitMoveScoring.get_attackable_units(self.unit, self.target_coord, self.game_state)
            if len(attackable_enemies) > 0:
                offensive_score += math.log2(len(attackable_enemies) + 1) * score_config.moveScore["off_attackable_enemy_units"]
                
                # Attackable Units                
                average_damage_inflicted = 0
                most_damage_inflicted = 0
                for tile_coord in attackable_enemies:
                    enemy_tile = self.game_state.map.get_tile_hex(*tile_coord)
                    current_tile = self.game_state.map.get_tile_hex(*self.target_coord)
                    enemy_unit = self.game_state.units.get_unit(enemy_tile.unit_id)
                    if self.unit.type == "Ranged":
                        damage_inflicted, damage_taken = CombatManager.estimate_combat(self.unit, enemy_unit, current_tile, enemy_tile, "ranged")
                    else:
                        damage_inflicted, damage_taken = CombatManager.estimate_combat(self.unit, enemy_unit, current_tile, enemy_tile, "melee")
                    average_damage_inflicted += damage_inflicted
                    most_damage_inflicted = max(most_damage_inflicted, damage_inflicted)

                offensive_score += average_damage_inflicted + most_damage_inflicted
                adjacent_tiles = utils.adjacent_tiles(self.target_coord)

                # Adjacent Enemies
                num_adjacent_units = 0
                for tile_coord in adjacent_tiles:
                    adjacent_tile = self.game_state.map.get_tile_hex(*tile_coord)
                    if adjacent_tile != None and adjacent_tile.unit_id != None:
                        tile_unit = self.game_state.units.get_unit(adjacent_tile.unit_id)
                        if tile_unit.owner_id != self.unit.owner_id:
                            num_adjacent_units += 1
                if num_adjacent_units > 0:
                    offensive_score += math.log2(len(attackable_enemies) + 1) * score_config.moveScore["off_adj_enemy_units"]
                
                
        # Health Multiplier
        unit_health_mult = score_config.moveScore["off_mult"] * ((self.unit.health - 50) / 50)
        offensive_score = offensive_score * unit_health_mult
        print(self.target_coord, "Off", offensive_score, unit_health_mult)
        self.score += offensive_score

    

    # Defensive Behavior
    # + Number of Adjacent Friendlies 
    # - Enemy potential damage to unit at tile
    # + Retaliatory Damage from unit at tile
    # Health Multiplier so this behavior is tuned down when higher health

    def defensive_score(self):  #Defensive Behavior
        defensive_score = 0
        reachable_tiles = UnitUtils.BFS_movement(self.unit, self.unit.movement, self.game_state)

        #Adjacent Friendlies
        for tile_coord in reachable_tiles:
            tile = self.game_state.map.get_tile_hex(*tile_coord)
            if tile.unit_id != None:
                tile_unit = self.game_state.units.get_unit(tile.unit_id)
                if tile_unit.owner_id == self.unit.owner_id:
                    defensive_score += score_config.moveScore["adjacent_friendlies"]

        #Enemy potential damage to unit at tile
        enemy_units = self.game_state.tile_attackable_by.get(self.target_coord, set())
        potential_damage_taken = 0
        potential_damage_inflicted = 0
        for enemy_unit_ids in enemy_units:
            enemy_unit = self.game_state.units.get_unit(enemy_unit_ids)
            enemy_tile = self.game_state.map.get_tile_hex(*enemy_unit.coord)
            current_tile = self.game_state.map.get_tile_hex(*self.target_coord)
            if self.unit.type == "Ranged":
                damage_inflicted, damage_taken = CombatManager.estimate_combat(enemy_unit, self.unit, enemy_tile, current_tile, "ranged")
            else:
                damage_inflicted, damage_taken = CombatManager.estimate_combat(enemy_unit, self.unit, enemy_tile, current_tile, "melee")
            potential_damage_taken += damage_inflicted
            potential_damage_inflicted += damage_taken

        #Potential Damage Taken
        defensive_score -= potential_damage_taken * score_config.moveScore["def_damage_taken_mult"]

        #Potential Damage inflicted back (good if in very defensible location)
        defensive_score += potential_damage_inflicted * score_config.moveScore["def_damage_inflicted_mult"]
        unit_health_mult = score_config.moveScore["off_mult"] * ((100 - self.unit.health - 50) / 50)
        defensive_score = defensive_score * unit_health_mult
        print(self.target_coord, "Def", defensive_score, unit_health_mult)
        self.score += defensive_score


    def distance_score(self):   #Score for how far target is
        pass