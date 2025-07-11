import interactions.utils as utils
import players.units_config as units_config
import heapq
from collections import deque
import map_generator.tile_types_config as tile_config
import random

#IGNORE FOR NOW. 


class MovementManager:
    def __init__(self, unit, map, unit_handler, player_handler, combat_manager):
        self.unit = unit
        self.map = map
        self.unit_handler = unit_handler
        self.player_handler = player_handler
        self.combat_manager = combat_manager
        
    def valid_destination(self, destination):

        # Gets visible and revealed tile for current player
        current_player = self.player_handler.get_player(self.unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles
        tile = self.map.get_tile_hex(*destination)

        # tile doesn't exist
        if tile is None:
            return False
        
        # destination is itself
        if destination == self.unit.coord:
            return False
        
        # tile visible and unreachable due to terrain
        if tile.get_coords() in visibile_tiles and tile.get_movement() == -1:
            return False
        
        # tile not visible
        if tile.get_coords() not in visibile_tiles:
            return True
        
        # tile visible
        if tile.get_coords() in revealed_tiles:
            # tile occupied by unit
            if tile.unit_id is not None:
                return False
        
        return True

    # Next tile in pre-calculated path is available. Important when unit has more movement than visibility and path goes thru impassable terrain or opposing units
    def valid_tile_move(self, next_tile):

        # Impassable Terrain (Mountain)
        if next_tile.get_movement() == -1:
            return False
        
        # Enemy unit occupies tile
        if next_tile.unit_id != None:
            next_tile_unit = self.unit_handler.get_unit(next_tile.unit_id)
            if next_tile_unit.owner_id != self.unit.owner_id:
                return False
        return True
    
    # Given player's knowledge, is a tile in an enemy's ZOC
    def zone_of_control(self, coord):
        if unit.follows_ZOC == False:
            return False
        current_player = self.player_handler.get_player(self.unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles

        # Loop thru adjacent tiles
        for neighbor_direction in utils.CUBE_DIRECTIONS_DICT.keys():
            neighbor = utils.CUBE_DIRECTIONS_DICT[neighbor_direction]
            neighbor_coord = tuple(x + y for x, y in zip(coord, neighbor))
            tile = self.map.get_tile_hex(*neighbor_coord)

            # Adjacent tile not visible
            if tile == None or tile.get_coords() not in visibile_tiles:
                continue
            unit = self.unit_handler.get_unit(tile.unit_id)

            # No enemy unit on adjacent tile
            if unit == None or unit.owner_id == unit.owner_id:
                continue
            elif unit.has_ZOC == True:
                return True
        return False

    # Simple heuristic for A*
    def hex_heuristic(self, a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2]))
    

    # A* for finding shortest path to destination given player's knowledge
    def A_star(self, destination, swap = False, attack = False):
        current_player = self.player_handler.get_player(self.unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles

        to_visit = []
        heapq.heappush(to_visit, (0, 0, self.unit.coord, None))
        visited = {}
        path = {}
        while to_visit:
            # Predicted Score, Distance to tile, Current Coord, Parent's Coord
            current_score, current_distance, current_coord, parent_coord = heapq.heappop(to_visit)

            # If tile has been reached in a more efficient manner already, then ignore and continue
            if current_coord in visited and current_distance >= visited[current_coord]:
                continue

            # Calculate movement left
            movement_remaining = (self.unit.movement - current_distance) % self.unit.movement

            # Is tile in ZOC
            enter_ZOC = self.zone_of_control(current_coord)

            path[current_coord] = parent_coord
            visited[current_coord] = current_distance

            # Destination reached
            if current_coord == destination:
                break

            # Neighboring tiles
            for neighbor_direction in utils.CUBE_DIRECTIONS_DICT.keys():
                neighbor = utils.CUBE_DIRECTIONS_DICT[neighbor_direction]
                neighbor_coord = tuple(x + y for x, y in zip(current_coord, neighbor))
                tile = self.map.get_tile_hex(*neighbor_coord)
                # Tile doesn't exist
                if tile is None:
                    continue
                
                if swap == True and tile.get_coords() not in visibile_tiles:
                    continue

                # Tile not revealed so assume cost of 1
                if tile.get_coords() not in revealed_tiles:
                    movement_cost = 1
                else:
                    # If visible, get movement
                    movement_cost = tile.get_movement(utils.OPPOSITE_EDGES[neighbor_direction])
                    if movement_cost == -1:
                        continue
                    movement_cost = min(self.unit.movement, movement_cost)

                # Make sure neighbor_coord not visited yet in a more efficient manner
                if (neighbor_coord not in visited or current_distance + movement_cost < visited.get(neighbor_coord, float('inf'))):
                    
                    #Add cost if not reachable in current turn
                    additional_cost = 0 if movement_remaining >= movement_cost else self.unit.movement - movement_remaining
                    temp_movement_remaining = movement_remaining
                    
                    #Allow unit to pass thru other units of same owner but not land on same tile
                    if tile.get_coords() in visibile_tiles:
                        if additional_cost > 0:
                            temp_movement_remaining = self.unit.movement
                        if attack == False and swap == False and temp_movement_remaining - movement_cost <= 0 and tile.unit_id is not None:
                            continue
                        if attack == False and tile.unit_id is not None and self.unit_handler.get_unit(tile.unit_id).owner_id != self.unit.owner_id:
                            continue

                    # Score to target and cost of reaching neighbor tile
                    score = current_distance + movement_cost + self.hex_heuristic(neighbor_coord, destination) + additional_cost
                    cost = current_distance + movement_cost + additional_cost

                    # Additional turn if prev tile is ZOC
                    cost += self.unit.movement if enter_ZOC else 0
                    
                    heapq.heappush(to_visit, (score, cost, neighbor_coord, current_coord))
        full_path = []

        if destination in path:
            current = destination
            while current != self.unit.coord:
                full_path.append(current)
                current = path[current]
            full_path.append(self.unit.coord)
            full_path.reverse()
        return full_path
    
    def turns_to_reach(self, destination, full_path):
        current_player = self.player_handler.get_player(self.unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles
        movement_left = self.unit.remaining_movement
        turn_reached = 0
        for x in range(len(full_path)):
            tile = self.map.get_tile_hex(*full_path[x])
            enter_ZOC = self.zone_of_control(tile.get_coords())
            if enter_ZOC and tile.get_coords() != self.unit.coord:
                movement_left = 0
            if tile.get_coords() == destination:
                return turn_reached + 1
            
            next_tile = self.map.get_tile_hex(*full_path[x + 1])
            direction = utils.get_relative_position(tile.get_coords(), next_tile.get_coords())
            direction = utils.OPPOSITE_EDGES[direction]
            if next_tile.get_coords() in revealed_tiles:
                next_tile_movement = min(self.unit.movement, next_tile.get_movement(direction))
            else:
                next_tile_movement = 1
            if movement_left - next_tile_movement < 0:
                turn_reached += 1
                movement_left = self.unit.movement - next_tile_movement
            else:
                movement_left -= next_tile_movement
        return -1
        
    def swap_units(self, destination, destination_unit):
        unit_1_path = self.A_star(destination, True)
        unit_2_path = destination_unit.A_star(self.unit.coord, True)
        if destination in unit_1_path:
            unit_1_turn_reached = self.turns_to_reach(destination, unit_1_path)
            unit_2_turn_reached = destination_unit.turns_to_reach(self.unit.coord, unit_2_path)
            if unit_1_turn_reached == 1 and unit_2_turn_reached == 1:
                destination_unit.swap_move(self.unit.coord, unit_2_path)
                self.swap_move(destination, unit_1_path)

            
    def swap_move(self, destination, full_path):
        current_player = self.player_handler.get_player(self.unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles
        movement_left = self.unit.remaining_movement
        turn_reached = 0
        orig_tile = self.map.get_tile_hex(*self.unit.coord)
        for x in range(len(full_path)):
            tile = self.map.get_tile_hex(*full_path[x])
            enter_ZOC = self.zone_of_control(tile.get_coords())
            if enter_ZOC and tile.get_coords() != self.unit.coord:
                movement_left = 0
            self.unit.coord = tile.get_coords()
            current_player.update_visibility()
            
            if tile.get_coords() == destination:
                tile.unit_id = self.unit.id
                self.unit.coord = tile.get_coords()
                break
            
            # Update visibility of unit at tile
            next_tile = self.map.get_tile_hex(*full_path[x + 1])
            # See if next tile is reachable. If not, then move unit to tile and redo A*.

            direction = utils.get_relative_position(tile.get_coords(), next_tile.get_coords())
            direction = utils.OPPOSITE_EDGES[direction]

            
            next_tile_movement = min(self.unit.movement, next_tile.get_movement(direction))
            
            
            movement_left -= next_tile_movement
        self.unit.remaining_movement = movement_left
        
    def move_to_helper(self, destination):
        destination_tile = self.map.get_tile_hex(*destination)
        if destination_tile != None and destination_tile.unit_id != None and not self.ZOC_locked:
            destination_unit = self.unit_handler.get_unit(destination_tile.unit_id)
            if destination_unit.owner_id == self.unit.owner_id:
                self.swap_units(destination, destination_unit)
                return self.unit.remaining_movement
                
        done_move = False
        while done_move == False:
            done_move = self.move_to(destination)
        return self.unit.remaining_movement



    # Will likely need to adjust this for units w/ more movement and less visibility. Need to make it so units gain visibility for each tile along path.
    # Current idea for move_to is A* -> move one tile -> gain visibility of tile -> A*, and repeat until either reached or out of movement
    def move_to(self, destination):

        #Given the player's current knowledge, is the destination reachable?
        if not self.valid_destination(destination):
            self.unit.destination = None
            self.unit.path = None
            return True
        self.unit.destination = destination
        full_path = self.A_star(destination)

        #Account for tile visibility
        current_player = self.player_handler.get_player(self.unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles

        #Find next tile for unit to move to
        if destination in full_path:
            self.unit.path = full_path
            movement_left = self.unit.remaining_movement
            if self.unit.ZOC_locked:
                movement_left = 0
            turn_reached = 0
            orig_tile = self.map.get_tile_hex(*self.unit.coord)
            for x in range(len(full_path)):
                tile = self.map.get_tile_hex(*full_path[x])
                enter_ZOC = self.zone_of_control(tile.get_coords())
                if enter_ZOC and tile.get_coords() != self.unit.coord:
                    self.unit.ZOC_locked = True
                    orig_tile.unit_id = None
                    tile.unit_id = self.unit.id
                    self.unit.coord = tile.get_coords()
                    break
                self.unit.coord = tile.get_coords()
                current_player.update_visibility()
                
                if (tile.x, tile.y, tile.z) == destination:
                    orig_tile.unit_id = None
                    tile.unit_id = self.unit.id
                    self.unit.coord = tile.get_coords()
                    break
                
                # Update visibility of unit at tile
                next_tile = self.map.get_tile_hex(*full_path[x + 1])
                # See if next tile is reachable. If not, then move unit to tile and redo A*.
                if self.valid_tile_move(next_tile) == False:
                    orig_tile.unit_id = None
                    tile.unit_id = self.unit.id
                    self.unit.remaining_movement = movement_left


                    return False


                direction = utils.get_relative_position(tile.get_coords(), next_tile.get_coords())
                direction = utils.OPPOSITE_EDGES[direction]

                
                next_tile_movement = min(self.unit.movement, next_tile.get_movement(direction))
                

                
                if movement_left - next_tile_movement < 0:
                    orig_tile.unit_id = None
                    tile.unit_id = self.unit.id
                    self.unit.coord = tile.get_coords()
                    break
                else:
                    movement_left -= next_tile_movement
            self.unit.remaining_movement = movement_left
        if self.unit.coord == self.unit.destination:
            self.unit.destination = None
            self.unit.path = None
        return True

                    
    def move_to_hover(self, destination):
        if self.unit.hover_destination != destination and self.unit.hover_destination is not None:
            self.clear_hover_path()
        destination_tile = self.map.get_tile_hex(*destination)
        if destination_tile != None and destination_tile.unit_id != None:
            destination_unit = self.unit_handler.get_unit(destination_tile.unit_id)
            if destination_unit.owner_id == self.unit.owner_id:
                self.unit.hover_destination = destination
                self.swap_hover(destination, destination_unit)
                return
        if not self.valid_destination(destination):
            return
        self.unit.hover_destination = destination
        full_path = self.A_star(destination)
        if destination in full_path:
            self.display_hover_path(full_path, destination)
    
    def swap_hover(self, destination, destination_unit):
        unit_1_path = self.A_star(destination, True)
        unit_2_path = destination_unit.A_star(self.unit.coord, True)
        if destination in unit_1_path:
            unit_1_turn_reached = self.turns_to_reach(destination, unit_1_path)
            unit_2_turn_reached = destination_unit.turns_to_reach(self.unit.coord, unit_2_path)
            if unit_1_turn_reached == 1 and unit_2_turn_reached == 1:
                self.display_hover_path(unit_1_path, destination)


    def clear_hover_path(self):
        if self.unit.hover_destination is not None:
            if self.unit.hover_path != None and len(self.unit.hover_path) > 0:
                for coord in self.unit.hover_path:
                    tile = self.map.get_tile_hex(*coord)
                    if tile is not None:
                        tile.path = False
                        tile.neighbor = None
                        tile.turn_reached = -1
            self.unit.hover_destination = None
            self.unit.hover_path = None
        
    def display_hover_path(self, full_path, destination):
        current_player = self.player_handler.get_player(self.unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles
        movement_left = self.unit.remaining_movement
        if self.unit.ZOC_locked:
            movement_left = 0
        turn_reached = 0
        for x in range(len(full_path)):
            tile = self.map.get_tile_hex(*full_path[x])
            enter_ZOC = self.zone_of_control(tile.get_coords())
            if enter_ZOC and tile.get_coords() != self.unit.coord:
                movement_left = 0
            if (tile.x, tile.y, tile.z) == destination:
                tile.path = True
                tile.turn_reached = turn_reached + 1
                break
            elif (tile.x, tile.y, tile.z) == self.unit.coord:
                tile.neighbor = self.map.get_tile_hex(*full_path[x + 1])
                tile.path = True
            else:
                tile.neighbor = self.map.get_tile_hex(*full_path[x + 1])
                tile.path = True
            
            next_tile = self.map.get_tile_hex(*full_path[x + 1])
            direction = utils.get_relative_position(tile.get_coords(), next_tile.get_coords())
            direction = utils.OPPOSITE_EDGES[direction]
            if next_tile.get_coords() in revealed_tiles:
                next_tile_movement = min(self.unit.movement, next_tile.get_movement(direction))
            else:
                next_tile_movement = 1
            if movement_left - next_tile_movement < 0:
                tile.turn_reached = turn_reached + 1
                turn_reached += 1
                movement_left = self.unit.movement - next_tile_movement
            else:
                movement_left -= next_tile_movement
        self.unit.hover_path = full_path