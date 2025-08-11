from units.units_utils import UnitUtils
from units.units_utils import UnitMove
from units.units_utils import UnitVisibility
from units.units_utils import UnitAttack
from units.units_utils import UnitScoringUtils
from units.units_utils import UnitMoveScoring
import utils as utils
import Scoring.score as scoring
import math
import sys
class Actions:

    #Culmination of actions
    def get_actions(player_id, game_state):
        tile_attackable_by = Actions.get_enemy_attackable_tiles(player_id, game_state)
        game_state.tile_attackable_by = tile_attackable_by
        player = game_state.players.get_player(player_id)
        legal_actions = []
        for unit_id in player.units:
            unit = game_state.units.get_unit(unit_id)
            print(f"Finding actions for {unit_id} at {unit.coord}")

            game_state.legal_moves_dict = {}
            action = UnitAction("Move", unit, game_state, unit.coord)
            game_state.legal_moves_dict[unit.coord] = action
            unit_legal_actions = UnitLegalActions(unit, player, game_state)
            if unit.AI_action == True and unit.ZOC_locked == False and unit.alive == True:
                legal_actions += unit_legal_actions.get_moves()
            if unit.AI_action == True and unit.alive == True:
                legal_actions += unit_legal_actions.get_attacks()
                legal_actions += unit_legal_actions.get_secondary()
            
        return legal_actions
        
    
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
    def __init__(self, unit, player, game_state):
        self.unit = unit
        self.player = player
        self.game_state = game_state

    def get_moves(self):
        visible_tiles = self.player.visible_tiles
        tiles = self.game_state.map.tiles
        legal_moves = []
        moveable_tiles = UnitScoringUtils.djikstra(self.unit, self.unit.coord, self.game_state)
        for tile_coord in tiles.keys():
            tile = self.game_state.map.get_tile_hex(*tile_coord)
            if tile_coord in moveable_tiles.keys() and (tile.unit_id == None or tile_coord not in visible_tiles):
                action = UnitAction("Move", self.unit, self.game_state, tile_coord)
                self.game_state.legal_moves_dict[tile_coord] = action
                legal_moves.append(action)
            elif UnitUtils.valid_swappable(self.unit, tile_coord, self.game_state):
                legal_moves.append(UnitAction("Swap", self.unit, self.game_state, tile_coord))
                pass
            
        for destination in self.game_state.legal_moves_dict.keys():
            full_path = []

            if destination in moveable_tiles:
                current = destination
                while current != self.unit.coord:
                    full_path.append(current)
                    current = moveable_tiles[current]
                full_path.append(self.unit.coord)
                full_path.reverse()
            #Account for tile visibility
            current_player = self.game_state.players.get_player(self.unit.owner_id)
            revealed_tiles = current_player.revealed_tiles
            visibile_tiles = current_player.visible_tiles

            #Find next tile for unit to move to
            #self.unit.path = full_path
            movement_left = self.unit.remaining_movement
            next_step_tile = self.unit.coord
            if self.unit.ZOC_locked:
                movement_left = 0
            for x in range(len(full_path)):
                tile = self.game_state.map.get_tile_hex(*full_path[x])
                enter_ZOC = UnitUtils.zone_of_control(self.unit, tile.get_coords(), self.game_state)
                if enter_ZOC and tile.get_coords() != self.unit.coord:
                    next_step_tile = tile.get_coords()
                    break
                
                if (tile.x, tile.y, tile.z) == destination:
                    next_step_tile = tile.get_coords()
                    break
                
                next_tile = self.game_state.map.get_tile_hex(*full_path[x + 1])


                direction = utils.get_relative_position(tile.get_coords(), next_tile.get_coords())
                direction = utils.OPPOSITE_EDGES[direction]

                
                next_tile_movement = min(self.unit.movement, next_tile.get_movement(direction))
                

                
                if movement_left - next_tile_movement < 0:
                    next_step_tile = tile.get_coords()
                    break
                else:
                    movement_left -= next_tile_movement
            try:
                self.game_state.legal_moves_dict[destination].score += self.game_state.legal_moves_dict[next_step_tile].score
            except:
                print("Destination", destination)
                print("Next Step", next_step_tile)
                print("Path", full_path)
                sys.exit(1)

        
        return legal_moves
    
    def get_attacks(self):
        attackable_enemies = UnitMoveScoring.get_attackable_units(self.unit, self.unit.coord, self.game_state)
        legal_moves = []
        for tile_coord in attackable_enemies:
            action = UnitAction("Attack", self.unit, self.game_state, tile_coord)
            legal_moves.append(action)
        return legal_moves
    
    def get_secondary(self):
        return [UnitAction("Fortify", self.unit, self.game_state)]



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
        elif self.type == "Swap":
            scorer = scoring.UnitMoveScore(self.unit, self.target, self.game_state)
            self.score = scorer.get_score()
            swap_tile = self.game_state.map.get_tile_hex(*self.target)
            swap_unit = self.game_state.units.get_unit(swap_tile.unit_id)
            scorer = scoring.UnitMoveScore(swap_unit, self.unit.coord, self.game_state)
            self.score = (scorer.get_score() + self.score) / 2
        elif self.type == "Attack":
            scorer = scoring.UnitAttackScore(self.unit, self.target, self.game_state)
            self.score = scorer.get_score()
        elif self.type == "Fortify":
            scorer = scoring.UnitFortifyScore(self.unit, self.game_state)
            self.score = scorer.get_score()



class CompleteUnitAction:
    def move_unit(unit, target):
        unit.move_to(target)
        if unit.remaining_movement == 0:
            unit.AI_action = False
    def swap_unit(unit, target):
        unit.move_to(target)
        if unit.remaining_movement == 0:
            unit.AI_action = False
    def attack(unit, target):
        unit.attack_enemy(target)
        unit.AI_action = False
    def fortify(unit):
        unit.fortify()
        unit.AI_action = False