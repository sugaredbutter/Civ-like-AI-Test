import interactions.utils as utils
import players.units_config as units_config
import heapq
from collections import deque
import map_generator.tile_types_config as tile_config

class Unit:
    def __init__(self, owner_id, id, type, health, vision, map, coord, unit_handler):
        self.owner_id = owner_id
        self.id = id
        self.type = type
        self.attack = units_config.units[type]["attack"]
        self.defense = units_config.units[type]["defense"]
        self.health = health
        self.vision = vision
        
        self.visible_tiles = set()

        self.map = map
        self.init_coord = coord
        self.coord = coord #(x, y, z)
        
        self.unit_handler = unit_handler
        self.hover_destination = None
        self.hover_path = None
        
        self.destination = None
        self.path = None

        self.alive = True
        self.fortified = False
        
        self.movement = units_config.units[type]["movement"]
        self.remaining_movement = self.movement
        
        self.skip_turn = False
    
    def remove(self):
        tile = self.map.get_tile_hex(*self.coord)
        tile.unit_id = None if tile.unit_id == self.id else tile.unit_id
        
    def reset_location(self):
        self.coord = self.init_coord
        tile = self.map.get_tile_hex(*self.coord)
        tile.unit_id = self.id
        self.destination = None
        self.path = None
        self.hover_destination = None
        self.hover_path = None      
        self.remaining_movement = self.movement  

    def valid_destination(self, destination):
        tile = self.map.get_tile_hex(*destination)
        if tile is None:
            return False
        # need to implement unit swapping 
        if tile.unit_id is not None:
            return False
        if destination == self.coord:
            return False
        if tile.get_movement() == -1:
            return False
        return True

    
    def hex_heuristic(self, a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2]))

    def A_star(self, destination):
        to_visit = []
        heapq.heappush(to_visit, (0, 0, self.coord, None))
        visited = {}
        path = {}
        while to_visit:
            current_score, current_distance, current_coord, parent_coord = heapq.heappop(to_visit)
            if current_coord in visited and current_distance >= visited[current_coord]:
                continue
            movement_remaining = (self.movement - current_distance) % self.movement
            #if movement_remaining == 0:
            #    movement_remaining = self.movement
            path[current_coord] = parent_coord
            visited[current_coord] = current_distance
            if current_coord == destination:
                break
            for neighbor_direction in utils.CUBE_DIRECTIONS_DICT.keys():
                neighbor = utils.CUBE_DIRECTIONS_DICT[neighbor_direction]
                neighbor_coord = tuple(x + y for x, y in zip(current_coord, neighbor))
                tile = self.map.get_tile_hex(*neighbor_coord)
                if tile is None:
                    continue
                movement_cost = tile.get_movement(utils.OPPOSITE_EDGES[neighbor_direction])
                if movement_cost == -1:
                    continue
                movement_cost = min(self.movement, movement_cost)
                if (neighbor_coord not in visited or current_distance + movement_cost < visited.get(neighbor_coord, float('inf'))):
                    
                    #Add cost if not reachable in current turn
                    additional_cost = 0 if movement_remaining >= movement_cost else self.movement - movement_remaining
                    temp_movement_remaining = movement_remaining
                    
                    #Allow unit to pass thru other units of same owner but not land on same tile
                    if additional_cost > 0:
                        temp_movement_remaining = self.movement
                    if temp_movement_remaining - movement_cost <= 0 and tile.unit_id is not None:
                        continue
                    if tile.unit_id is not None and self.unit_handler.get_unit(tile.unit_id).owner_id != self.owner_id:
                        continue
                    heapq.heappush(to_visit, (current_distance + movement_cost + self.hex_heuristic(neighbor_coord, destination) + additional_cost, current_distance + movement_cost + additional_cost, neighbor_coord, current_coord))
        return path
        
    def move_to(self, destination):
        if not self.valid_destination(destination):
            self.destination = None
            self.path = None
            return
        self.destination = destination
        path = self.A_star(destination)
        
        if destination in path:
            current = destination
            full_path = []
            while current != self.coord:
                full_path.append(current)
                current = path[current]
            full_path.append(self.coord)
            full_path.reverse()
            self.path = full_path
            movement_left = self.remaining_movement
            turned_reached = 0
            orig_tile = self.map.get_tile_hex(*self.coord)
            for x in range(len(full_path)):
                tile = self.map.get_tile_hex(*full_path[x])
                if (tile.x, tile.y, tile.z) == destination:
                    orig_tile.unit_id = None
                    tile.unit_id = self.id
                    self.coord = (tile.x, tile.y, tile.z)
                    break
                
                next_tile = self.map.get_tile_hex(*full_path[x + 1])
                direction = utils.get_relative_position(tile.get_coords(), next_tile.get_coords())
                direction = utils.OPPOSITE_EDGES[direction]
                next_tile_movement = min(self.movement, next_tile.get_movement(direction))
                if movement_left - next_tile_movement < 0:
                    orig_tile.unit_id = None
                    tile.unit_id = self.id
                    self.coord = (tile.x, tile.y, tile.z)
                    break
                else:
                    movement_left -= next_tile_movement
            self.remaining_movement = movement_left
        if self.coord == self.destination:
            self.destination = None
            self.path = None
        return self.remaining_movement

                    
    def move_to_hover(self, destination):
        if self.hover_destination != destination and self.hover_destination is not None:
            self.clear_hover_path()
        if not self.valid_destination(destination):
            return
            
        self.hover_destination = destination
        path = self.A_star(destination)
        if destination in path:
            current = destination
            full_path = []
            while current != self.coord:
                full_path.append(current)
                current = path[current]
            full_path.append(self.coord)
            full_path.reverse()
            self.display_hover_path(full_path, destination)
            

    def clear_hover_path(self):
        if self.hover_destination is not None:
            if self.hover_path != None and len(self.hover_path) > 0:
                for coord in self.hover_path:
                    tile = self.map.get_tile_hex(*coord)
                    if tile is not None:
                        tile.path = False
                        tile.neighbor = None
                        tile.turn_reached = -1
            self.hover_destination = None
            self.hover_path = None
        
    def display_hover_path(self, full_path, destination):
        movement_left = self.movement
        turned_reached = 0
        for x in range(len(full_path)):
            tile = self.map.get_tile_hex(*full_path[x])
            if (tile.x, tile.y, tile.z) == destination:
                tile.path = True
                tile.turn_reached = turned_reached + 1
                break
            elif (tile.x, tile.y, tile.z) == self.coord:
                tile.neighbor = self.map.get_tile_hex(*full_path[x + 1])
                tile.path = True
            else:
                tile.neighbor = self.map.get_tile_hex(*full_path[x + 1])
                tile.path = True
            
            next_tile = self.map.get_tile_hex(*full_path[x + 1])
            direction = utils.get_relative_position(tile.get_coords(), next_tile.get_coords())
            direction = utils.OPPOSITE_EDGES[direction]
            next_tile_movement = min(self.movement, next_tile.get_movement(direction))
            if movement_left - next_tile_movement < 0:
                tile.turn_reached = turned_reached + 1
                turned_reached += 1
                movement_left = self.movement - next_tile_movement
                print(tile.x, tile.y, tile.z, "Turn Reached", tile.turn_reached)
            else:
                movement_left -= next_tile_movement
        self.hover_path = full_path
    
    def end_turn(self):
        if self.remaining_movement > 0 and self.destination is not None:
            if self.coord != self.destination:
                self.move_to(self.destination)
                
    
    def turn_begin(self):
        self.remaining_movement = self.movement
        self.skip_turn = False
    
    def get_visibility(self):
        tile = self.map.get_tile_hex(*self.coord)
        visibility = self.vision + tile_config.biomes[tile.biome]["Terrain"][tile.terrain]["visibility_bonus"]
        
        visibile = set()
        queue = deque()
        queue.append((self.coord, visibility, self.vision))
        while queue:
            current_coord, visibility, distance = queue.popleft()
            visibile.add(current_coord) 
            print(current_coord, visibility, distance)
            if distance - 1 < 0:
                continue
            for neighbor_direction in utils.CUBE_DIRECTIONS_DICT.keys():
                neighbor = utils.CUBE_DIRECTIONS_DICT[neighbor_direction]
                neighbor_coord = tuple(x + y for x, y in zip(current_coord, neighbor))
                tile = self.map.get_tile_hex(*neighbor_coord)     
                if tile is not None and tile.get_coords() not in visibile:  
                    neighbor_visibility_bonus = tile_config.biomes[tile.biome]["Terrain"][tile.terrain]["visibility_bonus"]
                    neighbor_visibility_penalty = tile_config.biomes[tile.biome]["Terrain"][tile.terrain]["visibility_penalty"]

                    if tile.feature != None:
                        neighbor_visibility_bonus += tile_config.biomes[tile.biome]["Feature"][tile.feature]["visibility_bonus"]
                        neighbor_visibility_penalty += tile_config.biomes[tile.biome]["Feature"][tile.feature]["visibility_penalty"]

                    if visibility + neighbor_visibility_bonus > 0:
                        queue.append((tile.get_coords(), visibility - neighbor_visibility_penalty, distance - 1))
        print(visibile)
        return visibile

        
    
class UnitHandler:
    def __init__(self, map):
        self.map = map
        self.units = {}
        self.id_counter = 0

    def add_unit(self, owner, type, coord):
        unit = Unit(owner, self.id_counter, type, units_config.units[type]["health"], units_config.units[type]["visibility"], self.map, coord, self)
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
    