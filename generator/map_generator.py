import math
import pygame
import utils as utils
import random
import map.tile_types_config as tile_types_config
import generator.map_generator_config as map_generator_config
import map.map as current_map
import config as config
import noise
from collections import deque
import heapq


class MapGenerator:
    def __init__(self):
        pass

    def generate_map(self, width, height):
        seed = map_generator_config.MapConfig["seed"]
        if seed == '':
            seed = random.randint(0, 2**32 - 1)
        self.rng = random.Random(seed)
        q_elevation_offset = self.rng.randint(-10000, 10000)
        r_elevation_offset = self.rng.randint(-10000, 10000)
        q_temperature_offset = self.rng.randint(-10000, 10000)
        r_temperature_offset = self.rng.randint(-10000, 10000)
        q_moisture_offset = self.rng.randint(-10000, 10000)
        r_moisture_offset = self.rng.randint(-10000, 10000)
        self.tiles = {}
        for row in range(height): 
            for column in range(width):     
                x, y, z = utils.coord_to_hex_coord(row, column)
                self.tiles[(x, y, z)] = current_map.Tile(x, y, z)
                self.tiles[(x, y, z)].elevation = self.hex_elevation(column, row, q_elevation_offset, r_elevation_offset)
                self.tiles[(x, y, z)].temperature = self.hex_temperature(column, row, q_temperature_offset, r_temperature_offset)
                self.tiles[(x, y, z)].moisture = self.hex_moisture(column, row, q_moisture_offset, r_moisture_offset)
                self.calc_tile_attributes(self.tiles[(x, y, z)])
        self.create_rivers()
        self.connect_traversable()
        return self.tiles

    def calc_tile_attributes(self, tile):
        self.set_tile_terrain(tile)
        self.set_tile_biome(tile)
        self.set_tile_feature(tile)

    def set_tile_terrain(self, tile):
        elevation = (map_generator_config.MapConfig["elevation"]["current"] - map_generator_config.MapConfig["elevation"]["default"]) * map_generator_config.Terrain["elevation"]["change"]
        hill_elevation = map_generator_config.Terrain["hill"]["level"]
        hill_elevation += (map_generator_config.MapConfig["hilliness"]["current"] - map_generator_config.MapConfig["hilliness"]["default"]) * map_generator_config.Terrain["hill"]["change"]
        hill_elevation -= elevation
        mountain_elevation = map_generator_config.Terrain["mountain"]["level"]
        mountain_elevation += (map_generator_config.MapConfig["mountainous"]["current"] - map_generator_config.MapConfig["mountainous"]["default"]) * map_generator_config.Terrain["mountain"]["change"]
        mountain_elevation -= elevation

        if tile.elevation >= hill_elevation:
            tile.terrain = "Hill"
        if tile.elevation >= mountain_elevation:
            tile.terrain = "Mountain"
    
    def set_tile_biome(self, tile):
        temperature = (map_generator_config.MapConfig["temperature"]["current"] - map_generator_config.MapConfig["temperature"]["default"]) * map_generator_config.Biome["temperature"]["change"]
        plain_temperature = map_generator_config.Biome["plain"]["level"]
        plain_temperature -= temperature
        if tile.temperature <= plain_temperature:
            tile.biome = "Plain"
        else:
            tile.biome = "Desert"

    def set_tile_feature(self, tile):
        moisture = (map_generator_config.MapConfig["moisture"]["current"] - map_generator_config.MapConfig["moisture"]["default"]) * map_generator_config.Feature["moisture"]["change"]
        tree_moisture = map_generator_config.Feature["forest"]["level"]
        tree_moisture -= moisture
        if tile.moisture > tree_moisture and tile.biome != "Desert" and tile.terrain != "Mountain":
            tile.feature = "Forest"
        self.set_movement(tile)

    def set_movement(self, tile):
        tile.movement = tile_types_config.biomes[tile.biome]["Terrain"][tile.terrain]["movement"]
        if tile.feature != None:
            tile.movement += tile_types_config.biomes[tile.biome]["Feature"][tile.feature]["movement"]
        if tile.movement == 0:
            tile.movement = 1



    def create_rivers(self):
        river_budget = map_generator_config.Feature["river"]["level"]
        river_budget += (map_generator_config.MapConfig["rivers"]["current"] - map_generator_config.MapConfig["rivers"]["default"]) * map_generator_config.Feature["river"]["change"]
        river_sources = []
        river_tiles = []
        river_source_scoring = self.score_river_source(river_sources, river_tiles)

        while len(river_source_scoring) > 0 and river_budget - len(river_tiles) > 5:
            start_tile_coord = river_source_scoring[0][1]
            path = self.create_river_path(start_tile_coord, [], set(), river_tiles)
            
            distance = self.set_rivers(path)
            river_tiles += path[0:distance]
            river_sources.append(path[0])
            river_source_scoring = self.score_river_source(river_sources, river_tiles)


    def score_river_source(self, river_source_nodes, invalid_sources):
        ROWS, COLUMNS = config.map_settings["tile_height"], config.map_settings["tile_width"]

        river_source_scoring = []
        for tile in self.tiles.keys():
            if tile in invalid_sources:
                continue
            for river in self.tiles[tile].rivers.keys():
                if self.tiles[tile].rivers[river] == True:
                    continue
            score = 0

            #Elevation
            score += self.tiles[tile].elevation

            #Promote Mountains
            if self.tiles[tile].terrain == "Mountain":
                score *= 2

            #Discourage tiles nearer to edge of map
            x, y = utils.hex_coord_to_coord(*tile)
            distance_from_edge = min(min(x - 0, COLUMNS - 1 - x), min(y - 0, ROWS - 1 - y)) + 1
            score *= (distance_from_edge / (distance_from_edge + 1))
    
            #Discourage tiles near existing source node
            for node in river_source_nodes:
                distance = self.hex_heuristic(tile, node)
                score *= (distance / (distance + 1))
            river_source_scoring.append((score, tile))
        river_source_scoring.sort(reverse=True)
        return river_source_scoring
            
    def hex_heuristic(self, a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2]))
    
    def create_river_path(self, current_tile_coord, current_path, invalid_tiles, river_tiles):

        current_path.append(current_tile_coord)
        if current_tile_coord in river_tiles:
            return current_path
        next_tiles_sorted = []
        for neighbor_direction in utils.CUBE_DIRECTIONS_DICT.keys():
            neighbor = utils.CUBE_DIRECTIONS_DICT[neighbor_direction]
            neighbor_coord = tuple(x + y for x, y in zip(current_tile_coord, neighbor))
            neighbor_tile = self.tiles.get(neighbor_coord, None)
            if neighbor_tile == None:
                return current_path
            if neighbor_coord not in invalid_tiles:
                next_tiles_sorted.append((neighbor_tile.elevation, neighbor_coord))
        next_tiles_sorted.sort(key = lambda x: x[0])

        for neighbor_direction in utils.CUBE_DIRECTIONS_DICT.keys():
            neighbor = utils.CUBE_DIRECTIONS_DICT[neighbor_direction]
            neighbor_coord = tuple(x + y for x, y in zip(current_tile_coord, neighbor))
            invalid_tiles.add(neighbor_coord)
        for elevation, coord in next_tiles_sorted:
            response = self.create_river_path(coord, current_path, invalid_tiles, river_tiles)
            if response != False:
                return response
        
        return False
    
    # River Goal:
        # Get to edge of map from start
        # Follow elevation as best as possible
        # If at local minimum, go to tile with least elevation gain given it follows other tile rules
        # If intersecting with existing river, then join it

    def set_rivers(self, path):
        next_directions = None
        for i, tile_coord in enumerate(path):
            tile = self.tiles[tile_coord]
            if i + 1 < len(path):
                next_tile = self.tiles[path[i + 1]]
                next_tile_direction = utils.get_relative_position(tile_coord, next_tile.get_coords())
            else:
                if next_directions == None:
                    branch = [0, 1, 2, 3, 4, 5] # River entering new tile will have 2 options to branch to
                    best_hex_river_edges = []
                    reached_edge = False
                    while(len(branch) > 0) and not reached_edge:
                        direction_index = self.rng.choice(branch)
                        branch.remove(direction_index)
                        increment_list = [-1, 1]
                        for increment in increment_list:
                            reached_edge, best_hex_river_edges = self.calc_hex_river(tile, direction_index, increment)
                            if reached_edge:
                                break
                    self.set_hex_river(tile, best_hex_river_edges)
                    return i + 1

                else:
                    branch = [0, 1] # River entering new tile will have 2 options to branch to
                    best_hex_river_edges = []
                    reached_edge = False
                    while(len(branch) > 0) and not reached_edge:
                        random_choice = self.rng.choice(branch)
                        branch.remove(random_choice)
                        direction_index = utils.DIRECTIONS.index(next_directions[random_choice])
                        increment = -1 if random_choice == 0 else 1
                        reached_edge, best_hex_river_edges = self.calc_hex_river(tile, direction_index, increment)
                    self.set_hex_river(tile, best_hex_river_edges)
                    return i + 1
            if next_directions == None:
                branch = [0, 1, 2, 3, 4, 5] # River entering new tile will have 2 options to branch to
                best_hex_river_edges = []
                continue_next_tile = False
                while(len(branch) > 0) and not continue_next_tile:
                    direction_index = self.rng.choice(branch)
                    branch.remove(direction_index)
                    increment_list = [-1, 1]
                    for increment in increment_list:
                        continue_next_tile, best_hex_river_edges = self.calc_hex_river(tile, direction_index, increment, next_tile_direction)
                        if continue_next_tile:
                            break
                self.set_hex_river(tile, best_hex_river_edges)
                if continue_next_tile:
                    next_directions = utils.RIVER_TILE_MAPPINGS[(next_tile_direction, best_hex_river_edges[-1])]
                else:
                    return i + 1

            else:
                branch = [0, 1] # River entering new tile will have 2 options to branch to
                best_hex_river_edges = []
                continue_next_tile = False
                while(len(branch) > 0) and not continue_next_tile:
                    random_choice = self.rng.choice(branch)
                    branch.remove(random_choice)
                    direction_index = utils.DIRECTIONS.index(next_directions[random_choice])
                    increment = -1 if random_choice == 0 else 1
                    continue_next_tile, best_hex_river_edges = self.calc_hex_river(tile, direction_index, increment, next_tile_direction)
                self.set_hex_river(tile, best_hex_river_edges)
                if continue_next_tile:
                    next_directions = utils.RIVER_TILE_MAPPINGS[(next_tile_direction, best_hex_river_edges[-1])]
                else:
                    return i + 1
                
        
    def calc_hex_river(self, tile, direction_index, increment, next_tile_direction = None):
        if next_tile_direction != None:
            hex_river_edges = []
            reached_next_tile = True
            hex_river_edges.append(utils.DIRECTIONS[direction_index])

            # Loop around hex until river can reach next tile
            count = 0
            while utils.RIVER_TILE_MAPPINGS.get((next_tile_direction, utils.DIRECTIONS[direction_index]), None) == None and count < 6:
                if tile.rivers[utils.DIRECTIONS[direction_index]] == True:
                    reached_next_tile = False
                    break
                direction_index += increment
                if direction_index == -1:
                    direction_index = 5
                elif direction_index == 6:
                    direction_index = 0
                hex_river_edges.append(utils.DIRECTIONS[direction_index])
                count += 1

            
            return (reached_next_tile, hex_river_edges)
        else:
            out_of_bound_tile_directions = []
            for neighbor_direction in utils.CUBE_DIRECTIONS_DICT.keys():
                neighbor = utils.CUBE_DIRECTIONS_DICT[neighbor_direction]
                neighbor_coord = tuple(x + y for x, y in zip(tile.get_coords(), neighbor))
                if self.tiles.get(neighbor_coord, None) == None:
                    out_of_bound_tile_directions.append(utils.get_relative_position(tile.get_coords(), neighbor_coord))
            
            hex_river_edges = []
            hex_river_edges.append(utils.DIRECTIONS[direction_index])
            reached_edge = False
            # Loop around hex until river can reach next tile
            count = 0
            while reached_edge == False and count < 6:
                if tile.rivers[utils.DIRECTIONS[direction_index]] == True:
                    break
                for directions in out_of_bound_tile_directions:
                    if utils.RIVER_TILE_MAPPINGS.get((directions, utils.DIRECTIONS[direction_index]), None) != None:
                        reached_edge = True
                        break
                direction_index += increment
                if direction_index == -1:
                    direction_index = 5
                elif direction_index == 6:
                    direction_index = 0
                hex_river_edges.append(utils.DIRECTIONS[direction_index])
                count += 1

            return (reached_edge, hex_river_edges)

    def set_hex_river(self, tile, edges):
        for edge in edges:
            neighbor_coord = utils.get_tile_via_edge(*tile.get_coords(), edge)
            neighbor_tile = self.tiles.get(neighbor_coord, None)
            tile.rivers[edge] = True        
            if neighbor_tile == None:
                return
            neighbor_edge = utils.OPPOSITE_EDGES[edge]
            neighbor_tile.rivers[neighbor_edge] = True
        

    def hex_elevation(self, q, r, q_offset, r_offset):
        scale = map_generator_config.Terrain["scale"]["level"]
        scale += (map_generator_config.MapConfig["elevation_scale"]["default"] - map_generator_config.MapConfig["elevation_scale"]["current"]) * map_generator_config.Terrain["scale"]["change"]

        octaves = map_generator_config.octaves
        persistence = map_generator_config.persistence
        lacunarity = map_generator_config.lacunarity

        return noise.pnoise2(
            q * scale + q_offset, r * scale + r_offset,
            octaves = map_generator_config.MapConfig["variability"]["current"],

        )
    
    def hex_temperature(self, q, r, q_offset, r_offset):
        scale = map_generator_config.Biome["scale"]["level"]
        scale += (map_generator_config.MapConfig["biome_scale"]["default"] - map_generator_config.MapConfig["biome_scale"]["current"]) * map_generator_config.Biome["scale"]["change"]
        octaves = map_generator_config.octaves
        persistence = map_generator_config.persistence
        lacunarity = map_generator_config.lacunarity

        return noise.pnoise2(
            q * scale + q_offset, r * scale + r_offset,   
        )
    
    def hex_moisture(self, q, r, q_offset, r_offset):
        scale = map_generator_config.Feature["scale"]["level"]
        scale += (map_generator_config.MapConfig["clumpiness"]["default"] - map_generator_config.MapConfig["clumpiness"]["current"]) * map_generator_config.Feature["scale"]["change"]
        octaves = map_generator_config.octaves
        persistence = map_generator_config.persistence
        lacunarity = map_generator_config.lacunarity

        return noise.pnoise2(
            q * scale + q_offset, r * scale + r_offset,   
            octaves = octaves,
            persistence = persistence,
            lacunarity = lacunarity,
        )

    def connect_traversable(self):
        #Find all pockets of traversable
        localized_areas = [] #Set of of lists
        visited_tiles = set()
        for tile_coord in self.tiles.keys():
            if tile_coord not in visited_tiles and self.tiles[tile_coord].movement != -1:
                new_area = self.BFS_area(tile_coord)
                visited_tiles.update(new_area)
                localized_areas.append(list(new_area))
        start_coord = localized_areas[0][0]
        if len(localized_areas) > 1:
            for index in range(1, len(localized_areas)):
                path = self.A_star_connect_areas(start_coord, localized_areas[index][0])
                for path_tile_coord in path:
                    tile = self.tiles[path_tile_coord]
                    if tile.movement == -1:
                        tile.terrain = "Hill"
                        self.set_tile_feature(tile)
                        self.set_movement(tile)
    def BFS_area(self, tile_coord):
        reachable = set()
        queue = deque()
        queue.append(tile_coord)
        while queue:
            current_coord = queue.popleft()
            if current_coord in reachable:
                continue
            reachable.add(current_coord)
            
            
            
            for neighbor_direction in utils.CUBE_DIRECTIONS_DICT.keys():
                neighbor = utils.CUBE_DIRECTIONS_DICT[neighbor_direction]
                neighbor_coord = tuple(x + y for x, y in zip(current_coord, neighbor))
                if self.tiles.get(neighbor_coord, None) is None or self.tiles[neighbor_coord].movement == -1:
                    continue
                
                queue.append(neighbor_coord)
        return reachable
    
    def A_star_connect_areas(self, tile_coord, target_coord):
        to_visit = []
        heapq.heappush(to_visit, (0, 0, tile_coord, None))
        visited = {}
        path = {}
        while to_visit:
            # Predicted Score, Distance to tile, Current Coord, Parent's Coord
            current_score, current_distance, current_coord, parent_coord = heapq.heappop(to_visit)

            # If tile has been reached in a more efficient manner already, then ignore and continue
            if current_coord in visited and current_distance >= visited[current_coord]:
                continue

            path[current_coord] = parent_coord
            visited[current_coord] = current_distance

            # Destination reached
            if current_coord == target_coord:
                break
            # Neighboring tiles
            for neighbor_direction in utils.CUBE_DIRECTIONS_DICT.keys():
                neighbor = utils.CUBE_DIRECTIONS_DICT[neighbor_direction]
                neighbor_coord = tuple(x + y for x, y in zip(current_coord, neighbor))
                tile = self.tiles.get(neighbor_coord, None)
                # Tile doesn't exist
                if tile is None:
                    continue
                

                # Make sure neighbor_coord not visited yet in a more efficient manner
                movement_cost = 1 if tile.movement == -1 else 0
                    
                # Score to target and cost of reaching neighbor tile
                score = current_distance + movement_cost + self.hex_heuristic(neighbor_coord, target_coord)
                cost = current_distance + movement_cost
                
                heapq.heappush(to_visit, (score, cost, neighbor_coord, current_coord))

        # Convert dict to list
        full_path = []
        if tile_coord in path:
            current = target_coord
            while current != tile_coord:
                full_path.append(current)
                current = path[current]
            full_path.append(tile_coord)
            full_path.reverse()
        return full_path
                






# Perlin Noise
# Terrain: Separate Perlin Noise
# Feature: Separate Perlin Noise
# River: Pathfinding from edge to edge with random branches? Perhaps take into account terrain or lowest terrain?
# Biome: Separate Perlin Noise
# Ensure all traversible tiles are reachable to one another
    # If tile is not reachable
