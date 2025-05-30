import interactions.utils as utils
import heapq

class Unit:
    def __init__(self, owner_id, id, type, health, map, coord):
        self.owner_id = owner_id
        self.id = id
        self.type = type
        self.health = health
        self.map = map
        self.coord = coord

        self.alive = True
        self.fortified = False
    
    def hex_heuristic(self, a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2]))

        
    def move_to(self, destination):
        to_visit = []
        heapq.heappush(to_visit, (self.hex_heuristic(self.coord, destination), self.coord))
        visited = set()
        path = {}
        while to_visit:
            current_distance, current_coord = heapq.heappop(to_visit)
            if current_coord == destination:
                break
            visited.add(current_coord)
            for neighbor in utils.CUBE_DIRECTIONS:
                neighbor_coord = tuple(x + y for x, y in zip(current_coord, neighbor))
                if self.map.get_tile_hex(*neighbor_coord) is not None and neighbor_coord not in visited:
                    if neighbor_coord not in to_visit:
                        heapq.heappush(to_visit, (current_distance + self.hex_heuristic(neighbor_coord, destination), neighbor_coord))
                        path[neighbor_coord] = current_coord
        
        if destination in path:
            current = destination
            full_path = []
            while current != self.coord:
                full_path.append(current)
                current = path[current]
            full_path.reverse()
            print(f"Path found: {full_path}")
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
            del self.units[id]
            print(len(self.units))

            return True
        return False
    
    