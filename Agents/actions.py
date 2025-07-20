from players.units_utils import UnitUtils
from players.units_utils import UnitMove
from players.units_utils import UnitVisibility
from players.units_utils import UnitAttack
from players.units_utils import UnitScoringUtils
from players.units_utils import UnitMoveScoring
import utils as utils
import Scoring.score as scoring
class Actions:

    #Culmination of actions
    def get_actions(player_id, game_state):
        tile_attackable_by = Actions.get_enemy_attackable_tiles(player_id, game_state)
        game_state.tile_attackable_by = tile_attackable_by
        return Actions.get_moves(player_id, game_state)
        

    #Tiles able to be moved to
    def get_moves(player_id, game_state):
        player = game_state.players.get_player(player_id)
        legal_actions = []
        for unit_id in player.units:
            unit = game_state.units.get_unit(unit_id)
            if unit.AI_action == True and unit.ZOC_locked == False:
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
        legal_moves_dict = {}
        action = UnitAction("Move", unit, game_state, unit.coord)
        legal_moves_dict[unit.coord] = action
        moveable_tiles = UnitScoringUtils.djikstra(unit, unit.coord, game_state)
        for tile_coord in tiles.keys():
            if tile_coord in moveable_tiles.keys():
                action = UnitAction("Move", unit, game_state, tile_coord)
                legal_moves_dict[tile_coord] = action
                legal_moves.append(action)
            elif UnitUtils.valid_swappable(unit, tile_coord, game_state):
                # legal_moves.append(UnitAction("Swap", unit, game_state, tile_coord))
                pass
        for destination in legal_moves_dict.keys():
            full_path = []

            if destination in moveable_tiles:
                current = destination
                while current != unit.coord:
                    full_path.append(current)
                    current = moveable_tiles[current]
                full_path.append(unit.coord)
                full_path.reverse()
            #Account for tile visibility
            current_player = game_state.players.get_player(unit.owner_id)
            revealed_tiles = current_player.revealed_tiles
            visibile_tiles = current_player.visible_tiles

            #Find next tile for unit to move to
            unit.path = full_path
            movement_left = unit.remaining_movement
            next_step_tile = unit.coord
            if unit.ZOC_locked:
                movement_left = 0
            for x in range(len(full_path)):
                tile = game_state.map.get_tile_hex(*full_path[x])
                enter_ZOC = UnitUtils.zone_of_control(unit, tile.get_coords(), game_state)
                if enter_ZOC and tile.get_coords() != unit.coord:
                    next_step_tile = tile.get_coords()
                    break
                
                if (tile.x, tile.y, tile.z) == destination:
                    next_step_tile = tile.get_coords()
                    break
                
                next_tile = game_state.map.get_tile_hex(*full_path[x + 1])


                direction = utils.get_relative_position(tile.get_coords(), next_tile.get_coords())
                direction = utils.OPPOSITE_EDGES[direction]

                
                next_tile_movement = min(unit.movement, next_tile.get_movement(direction))
                

                
                if movement_left - next_tile_movement < 0:
                    next_step_tile = tile.get_coords()
                    break
                else:
                    movement_left -= next_tile_movement
            legal_moves_dict[destination].score += legal_moves_dict[next_step_tile].score

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
