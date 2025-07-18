import Scoring.score_config as score_config
import utils as utils
import math
from players.units_utils import UnitUtils
from players.units_utils import UnitMove
from players.units_utils import UnitVisibility
from players.units_utils import UnitAttack

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
        self.adjacency_score()
        self.offensive_score()
        self.defensive_score()
        self.distance_score()
        return self.score
        
    def exploration_score(self):    #Score for exploring new lands
        revealed_tiles = self.player.revealed_tiles
        if self.target_coord not in revealed_tiles:
            self.score += score_config.moveScore["unrevealed"]
        
    def adjacency_score(self):  #Score for being near other friendly units
        reachable_tiles = UnitUtils.BFS_movement(self.unit, self.unit.movement, self.game_state)
        for tile_coord in reachable_tiles:
            tile = self.game_state.map.get_tile_hex(*tile_coord)
            if tile.unit_id != None:
                tile_unit = self.game_state.units.get_unit(tile.unit_id)
                if tile_unit.owner_id == self.unit.owner_id:
                    self.score += score_config.moveScore["adjacent_friendlies"]

    def offensive_score(self):  #Score for being near enemies/approaching them
        offensive_score = 0
        if self.unit.type != "ranged":
            attackable_enemies = UnitAttack.get_attackable_units(self.unit, self.game_state, True)
            if len(attackable_enemies) > 0:
                offensive_score += math.log2(len(attackable_enemies) + 1) * score_config.moveScore["off_attackable_enemy_units"]
                print(attackable_enemies, offensive_score)
        self.score += offensive_score

    # enemies able to be attacked
    # adjacent units (important for ranged units since they are weaker at defending)
    # type of unit (don't wanna get too close if unit is ranged for example)
    # Health scaling (tunes down offensive score if unit is lower health for example (not too aggressive)
    # Nearby Friendly Units vs Enemy Units. Hopefully prefers attacking in groups.    
    def defensive_score(self):  #Score for retreating/advantageous location
        pass    
    def distance_score(self):   #Score for how far target is
        pass