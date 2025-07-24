import utils as utils
import players.units_config as units_config
import heapq
from collections import deque
import map_generator.tile_types_config as tile_config
import random
from players.units_utils import UnitUtils
from players.units_utils import UnitMove
from players.units_utils import UnitVisibility
from players.units_utils import UnitAttack

from combat_manager.combat_manager import CombatManager
class Unit:
    def __init__(self, owner_id, id, type, health, vision, coord, visual_effects, game_state):
        self.visual_effects = visual_effects
        self.owner_id = owner_id
        self.id = id
        self.type = type    #Melee, Ranged, Cavalry 
        self.attack = units_config.units[type]["attack"]
        self.defense = units_config.units[type]["defense"]
        self.range = units_config.units[type].get("range", None)
        self.health = random.randint(1, 100)
        self.orig_health = self.health
        self.combat_type = units_config.units[type]["combat_type"]


        self.vision = vision
        self.has_ZOC = units_config.units[type]["defense_zoc"]
        self.follows_ZOC = units_config.units[type]["attack_zoc"]
        
        self.attackable_tiles = set()

        self.init_coord = coord
        self.coord = coord #(x, y, z)
        
        self.hover_destination = None
        self.hover_path = None
        
        self.destination = None
        self.path = None

        self.alive = True
        
        self.fortified = False
        self.turns_fortified = 0
        
        self.fortify_and_heal = False
        
        self.skip = False
        
        self.ZOC_locked = False
        
        self.movement = units_config.units[type]["movement"]
        self.remaining_movement = self.movement
        
        self.action = True

        self.game_state = game_state   


        #AI stuff
        self.AI_action = True
        self.AI_last_move = None

    def remove(self):
        tile = self.game_state.map.get_tile_hex(*self.coord)
        tile.unit_id = None if tile.unit_id == self.id else tile.unit_id
        
    # End of game so reset units to original pos
    def reset_location(self):
        self.coord = self.init_coord
        tile = self.game_state.map.get_tile_hex(*self.coord)
        tile.unit_id = self.id
        self.destination = None
        self.path = None
        self.hover_destination = None
        self.hover_path = None      
        self.remaining_movement = self.movement 
        self.health = self.orig_health
        self.ZOC_locked = False
        self.fortified = False
        self.action = True
        self.fortify_and_heal = False
        self.turns_fortified = 0
        self.skip = False
    
        
    def move_to(self, destination):
        destination_tile = self.game_state.map.get_tile_hex(*destination)
        current_player = self.game_state.players.get_player(self.owner_id)
        if destination_tile != None and destination_tile.unit_id != None and not self.ZOC_locked:
            destination_unit = self.game_state.units.get_unit(destination_tile.unit_id)
            if destination_unit.owner_id == self.owner_id:
                UnitMove.swap_units(self, destination, destination_unit, self.game_state)
                current_player.update_visibility()
                return self.remaining_movement
                
        done_move = False
        while done_move == False:
            done_move = UnitMove.move_to(self, destination, self.game_state)
        if self.remaining_movement > 0:
            self.action = True
        else:
            self.action = False
        current_player.update_visibility()
        return self.remaining_movement

                    
    def move_to_hover(self, destination):
        if self.hover_destination != destination and self.hover_destination is not None:
            UnitMove.clear_hover_path(self, self.game_state)
        destination_tile = self.game_state.map.get_tile_hex(*destination)
        if destination_tile != None and destination_tile.unit_id != None:
            destination_unit = self.game_state.units.get_unit(destination_tile.unit_id)
            if destination_unit.owner_id == self.owner_id:
                self.hover_destination = destination
                UnitMove.swap_hover(self, destination, destination_unit, self.game_state)
                return
        if not UnitUtils.valid_destination(self, destination, self.game_state):
            return
        self.hover_destination = destination
        full_path = UnitUtils.A_star(self, destination, self.game_state)
        if destination in full_path:
            UnitMove.display_hover_path(self, full_path, destination, self.game_state)
    
    def end_turn(self):
        if self.alive == False:
            return
        if self.remaining_movement > 0 and self.destination is not None and not self.ZOC_locked:
            if self.coord != self.destination:
                self.move_to(self.destination)
        if self.remaining_movement > 0 and not self.fortified:
            self.skip = True
            self.fortified = True
                
    
    def turn_begin(self):
        if self.alive == False:
            return
        self.ZOC_locked = False
        if self.fortified:
            health_healed = 5 * (self.remaining_movement / self.movement) + min(10, self.turns_fortified * 5)
            self.visual_effects.add_heal(health_healed, self.coord)
            self.health = min(self.health + health_healed, 100)
            if self.health == 100 and self.fortify_and_heal:
                self.fortify_and_heal = False
                self.fortified = False
                self.action = True
        if self.skip:
            self.fortified = False
            self.skip = False
        if not self.fortified:
            self.action = True
        else:
            self.turns_fortified += 1
        self.remaining_movement = self.movement
        self.AI_action = True
            

    
    def get_visibility(self):
        tile = self.game_state.map.get_tile_hex(*self.coord)
        visibility = self.vision + tile_config.biomes[tile.biome]["Terrain"][tile.terrain]["visibility_bonus"]
        return UnitVisibility.BFS_visibility(self, visibility, self.game_state)
    
    
    def attack_hover(self, destination):
        if self.hover_destination != destination and self.hover_destination is not None:
            UnitMove.clear_hover_path(self, self.game_state)
        attackable_tiles = UnitAttack.get_attackable_units(self, self.game_state)
        if destination not in attackable_tiles or self.remaining_movement == 0:
            return None
        if self.combat_type == "melee":
            full_path = UnitUtils.A_star(self, destination, self.game_state, False, True)
            current_player = self.game_state.players.get_player(self.owner_id)
            revealed_tiles = current_player.revealed_tiles
            visibile_tiles = current_player.visible_tiles

            for x in range(len(full_path)):
                tile = self.game_state.map.get_tile_hex(*full_path[x])
                if (tile.x, tile.y, tile.z) == destination:
                    tile.path = True
                    break
                elif (tile.x, tile.y, tile.z) == self.coord:
                    tile.neighbor = self.game_state.map.get_tile_hex(*full_path[x + 1])
                    tile.path = True
                else:
                    tile.neighbor = self.game_state.map.get_tile_hex(*full_path[x + 1])
                    tile.path = True
                
            self.hover_destination = destination
            self.hover_path = full_path
        enemy_tile = self.game_state.map.get_tile_hex(*destination)
        current_tile = self.game_state.map.get_tile_hex(*self.coord)
        enemy_unit = self.game_state.units.get_unit(enemy_tile.unit_id)
        if self.type == "Ranged":
            damage_inflicted, damage_taken = CombatManager.estimate_combat(self, enemy_unit, current_tile, enemy_tile, "ranged")
            self_CS, enemy_CS = CombatManager.get_combat_strength(self, enemy_unit, current_tile, enemy_tile, "ranged")
            self_CS_bonus, enemy_CS_bonus = CombatManager.get_combat_bonus(self, enemy_unit, current_tile, enemy_tile, "ranged")
            return(damage_inflicted, 0, self, enemy_unit, self_CS, enemy_CS, self_CS_bonus, enemy_CS_bonus)
        else:
            damage_inflicted, damage_taken = CombatManager.estimate_combat(self, enemy_unit, current_tile, enemy_tile, "melee")
            self_CS, enemy_CS = CombatManager.get_combat_strength(self, enemy_unit, current_tile, enemy_tile, "melee")
            self_CS_bonus, enemy_CS_bonus = CombatManager.get_combat_bonus(self, enemy_unit, current_tile, enemy_tile, "melee")
            return(damage_inflicted, damage_taken, self, enemy_unit, self_CS, enemy_CS, self_CS_bonus, enemy_CS_bonus)


    def attack_enemy(self, destination):
        if self.type == "Ranged":
            UnitAttack.ranged_attack(self, destination, self.game_state, self.visual_effects)
        else:
            UnitAttack.melee_attack(self, destination, self.game_state, self.visual_effects)
        if self.remaining_movement > 0:
            self.action = True
        else:
            self.action = False
        self.fortified = False
        self.turns_fortified = 0
        current_player = self.game_state.players.get_player(self.owner_id)
        current_player.update_visibility()
        return self.remaining_movement

            
    def fortify(self):
        if self.remaining_movement > 0:
            self.path = None
            self.destination = None
            self.fortified = True
            self.action = False
    
    def heal(self):
        if self.remaining_movement > 0:
            self.path = None
            self.destination = None
            self.fortified = True
            self.fortify_and_heal = True
            self.action = False
            
    def cancel_action(self):
        self.path = None
        self.destination = None
        self.fortified = False
        self.fortify_and_heal = False
        self.turns_fortified = 0
        if self.remaining_movement > 0:
            self.action = True
    
    def skip_turn(self):
        if self.remaining_movement > 0:
            self.path = None
            self.destination = None
            self.fortified = True
            self.skip = True
            self.action = False
            
    

            


  
    
class UnitHandler:
    def __init__(self, visual_effects):
        self.visual_effects = visual_effects
        self.units = {}
        self.id_counter = 0
        self.game_state = None

    def add_unit(self, owner, type, coord):
        unit = Unit(owner, self.id_counter, type, units_config.units[type]["health"], units_config.units[type]["visibility"], coord, self.visual_effects, self.game_state)
        self.units[unit.id] = unit
        self.id_counter += 1
        return unit.id

    def get_unit(self, id):
        return self.units.get(id, None)

    def remove_unit(self, id):
        if id in self.units:
            self.units[id].remove()
            del self.units[id]
            return True
        return False
    
    def end_game_reset(self):
        for unit in self.units.values():
            unit.reset_location()
    