from players.units_utils import UnitUtils
from players.units_utils import UnitMove
from players.units_utils import UnitVisibility
from players.units_utils import UnitAttack
from players.units_utils import UnitMoveScoring
import Scoring.score as scoring
class Actions:

    #Culmination of actions
    def get_actions(player_id, game_state):
        tile_attackable_by = Actions.get_enemy_attackable_tiles(player_id, game_state)
        game_state.tile_attackable_by = tile_attackable_by
        print("Enemy Attackable Tiles: ", tile_attackable_by)
        return Actions.get_moves(player_id, game_state)
        

    #Tiles able to be moved to
    def get_moves(player_id, game_state):
        player = game_state.players.get_player(player_id)
        legal_actions = []
        for unit_id in player.units:
            unit = game_state.units.get_unit(unit_id)
            if unit.AI_action == True:
                legal_actions += UnitLegalActions.get_moves(unit, game_state)
        return legal_actions

    #Units able to be attacked
    def get_attacks(self):
        pass

    #Fortify, Heal, Skip, etc
    def get_secondary_actions(self):
        pass
    
    def get_enemy_attackable_tiles(player_id, game_state):
        player = game_state.players.get_player(player_id)
        tile_attackable_by = {}
        visible_tiles = player.visible_tiles
        for tile_coord in visible_tiles:
            tile = game_state.map.get_tile_hex(*tile_coord)
            if tile.unit_id is not None:
                unit = game_state.units.get_unit(tile.unit_id)
                if unit.owner_id != player_id:
                    enemy_attackable_tiles = UnitMoveScoring.get_attackable_tiles(unit, tile_coord, game_state)
                    enemy_attackable_tiles &= visible_tiles
                    for enemy_attackable_tile in enemy_attackable_tiles:
                        if tile_attackable_by.get(enemy_attackable_tile, None) is None:
                            tile_attackable_by[enemy_attackable_tile] = {tile.unit_id}
                        else:
                            tile_attackable_by[enemy_attackable_tile].add(tile.unit_id)

                        
                        
        return tile_attackable_by
                    
        

class UnitLegalActions:
    def get_moves(unit, game_state):
        tiles = game_state.map.tiles
        legal_moves = []
        for tile_coord in tiles.keys():
            if UnitUtils.valid_destination(unit, tile_coord, game_state):
                legal_moves.append(UnitAction("Move", unit, game_state, tile_coord))
            elif UnitUtils.valid_swappable(unit, tile_coord, game_state):
                # legal_moves.append(UnitAction("Swap", unit, game_state, tile_coord))
                pass
                
        return legal_moves



class UnitAction:
    def __init__(self, type, unit, game_state, target = None):
        self.type = type    #move, swap_move, attack
        self.unit = unit
        self.score = 0
        self.game_state = game_state
        self.target = target
        self.get_score()

    def get_score(self):
        if self.type == "Move":
            scorer = scoring.UnitMoveScore(self.unit, self.target, self.game_state)
            self.score = scorer.get_score()


class CompleteUnitAction:
    def move_unit(unit, target):
        unit.move_to(target)
        if unit.remaining_movement == 0:
            unit.AI_action = False
