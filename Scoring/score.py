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
        
    def offensive_score(self):  #Score for being near enemies/approaching them
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
        unit_health_mult = score_config.moveScore["off_mult"] * (self.unit.health / 50)
        offensive_score * unit_health_mult
        self.score += offensive_score

    # enemies able to be attacked
    # type of unit (don't wanna get too close if unit is ranged for example)
    # Health scaling (tunes down offensive score if unit is lower health for example (not too aggressive)
    # Nearby Friendly Units vs Enemy Units. Hopefully prefers attacking in groups.    

    def defensive_score(self):  #Reasons for not choosing that tile (due to weakness/other reasons)
        defensive_score = 0
        reachable_tiles = UnitUtils.BFS_movement(self.unit, self.unit.movement, self.game_state)
        for tile_coord in reachable_tiles:
            tile = self.game_state.map.get_tile_hex(*tile_coord)
            if tile.unit_id != None:
                tile_unit = self.game_state.units.get_unit(tile.unit_id)
                if tile_unit.owner_id == self.unit.owner_id:
                    defensive_score += score_config.moveScore["adjacent_friendlies"]
        defensive_score -= len(self.game_state.tile_attackable_by.get(self.target_coord, set())) * score_config.moveScore["def_num_attackable_by_penalty"]
        unit_health_mult = score_config.moveScore["off_mult"] * ((100 - self.unit.health) / 50)
        defensive_score * unit_health_mult
        self.score += defensive_score

        

    def distance_score(self):   #Score for how far target is
        pass