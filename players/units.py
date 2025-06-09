import interactions.utils as utils
import players.units_config as units_config
import heapq

class Unit:
    def __init__(self, owner_id, id, type, health, map, coord):
        self.owner_id = owner_id
        self.id = id
        self.type = type
        self.health = health
        self.map = map
        self.init_coord = coord
        self.coord = coord
        
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
            if movement_remaining == 0:
                movement_remaining = self.movement
            path[current_coord] = parent_coord
            visited[current_coord] = current_distance
            if current_coord == destination:
                break
            for neighbor in utils.CUBE_DIRECTIONS:
                neighbor_coord = tuple(x + y for x, y in zip(current_coord, neighbor))
                tile = self.map.get_tile_hex(*neighbor_coord)
                if tile is not None and (neighbor_coord not in visited or current_distance + tile.movement < visited.get(neighbor_coord, float('inf'))):
                    additional_cost = 0 if movement_remaining >= tile.movement else self.movement - movement_remaining
                    temp_movement_remaining = movement_remaining
                    if additional_cost > 0:
                        temp_movement_remaining = self.movement
                    if temp_movement_remaining - tile.movement <= 0 and tile.unit_id is not None:
                        continue
                    heapq.heappush(to_visit, (current_distance + tile.movement + self.hex_heuristic(neighbor_coord, destination) + additional_cost, current_distance + tile.movement + additional_cost, neighbor_coord, current_coord))
        return path
        
    def move_to(self, destination):
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

                    
    def move_to_hover(self, destination):
        if self.hover_destination != destination and self.hover_destination is not None:
            self.clear_hover_path()
            
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
            movement_left = self.movement
            turned_reached = 0
            for x in range(len(full_path)):
                tile = self.map.get_tile_hex(*full_path[x])
                if (tile.x, tile.y, tile.z) == destination:
                    tile.path = True
                    break
                elif (tile.x, tile.y, tile.z) == self.coord:
                    tile.neighbor = self.map.get_tile_hex(*full_path[x + 1])
                    tile.path = True
                else:
                    tile.neighbor = self.map.get_tile_hex(*full_path[x + 1])
                    tile.path = True
                
                next_tile = self.map.get_tile_hex(*full_path[x + 1])
                if movement_left - next_tile.movement < 0:
                    tile.turn_reached = turned_reached + 1
                    turned_reached += 1
                    movement_left = self.movement - next_tile.movement
                    print(tile.x, tile.y, tile.z, "Turn Reached", tile.turn_reached)
                else:
                    movement_left -= next_tile.movement
            self.hover_path = full_path

        
    def clear_hover_path(self):
        if self.hover_destination is not None:
            if self.hover_path != None and len(self.hover_path) > 0:
                for coord in self.hover_path:
                    tile = self.map.get_tile_hex(*coord)
                    if tile is not None:
                        tile.path = False
                        tile.neighbor = None
            self.hover_destination = None
            self.hover_path = None
        
class UnitHandler:
    def __init__(self, map):
        self.map = map
        self.units = {}
        self.id_counter = 0

    def add_unit(self, owner, type, health, coord):
        unit = Unit(owner, self.id_counter, type, health, self.map, coord)
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
    