import math
import pygame
import utils as utils
import random
import map_generator.tile_types_config as tile_types_config
import map_generator.map_generator_config as map_generator_config
import map_generator.map as current_map
import config as config
import noise

class MapGenerator:
    def __init__(self):
        pass

    def generate_map(self, width, height):
        seed = map_generator_config.MapConfig["seed"]
        print("Seed", seed)
        self.rng = random.Random(seed) if seed != '' else random.Random()
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
        return self.tiles

    def calc_tile_attributes(self, tile):
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

        temperature = (map_generator_config.MapConfig["temperature"]["current"] - map_generator_config.MapConfig["temperature"]["default"]) * map_generator_config.Biome["temperature"]["change"]
        plain_temperature = map_generator_config.Biome["plain"]["level"]
        plain_temperature -= temperature
        if tile.temperature <= plain_temperature:
            tile.biome = "Plain"
        else:
            tile.biome = "Desert"

        moisture = (map_generator_config.MapConfig["moisture"]["current"] - map_generator_config.MapConfig["moisture"]["default"]) * map_generator_config.Feature["moisture"]["change"]
        tree_moisture = map_generator_config.Feature["forest"]["level"]
        tree_moisture -= moisture
        if tile.moisture > tree_moisture and tile.biome != "Desert" and tile.terrain != "Mountain":
            tile.feature = "Forest"


    def create_rivers(self):
        river_budget = map_generator_config.Feature["river"]["level"]
        river_budget += (map_generator_config.MapConfig["rivers"]["current"] - map_generator_config.MapConfig["rivers"]["default"]) * map_generator_config.Feature["river"]["change"]
        river_sources = []
        for key in self.tiles:
            if self.tiles[key].terrain == "Mountain":
                river_sources.append(key)

        random_start = random.choice(river_sources)
        river_tiles = []
        start_tile_coord = random_start
        path = self.create_river_path(start_tile_coord, [], set(), river_tiles)
        river_tiles += path
        print(path)
        self.set_rivers(path)
    
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
                        print("1")
                        direction_index = random.choice(branch)
                        branch.remove(direction_index)
                        increment_list = [-1, 1]
                        for increment in increment_list:
                            reached_edge, best_hex_river_edges = self.calc_hex_river(tile, direction_index, increment)
                            if reached_edge:
                                break
                    self.set_hex_river(tile, best_hex_river_edges)
                    return i

                else:
                    branch = [0, 1] # River entering new tile will have 2 options to branch to
                    best_hex_river_edges = []
                    reached_edge = False
                    while(len(branch) > 0) and not reached_edge:
                        print("2")
                        random_choice = random.choice(branch)
                        branch.remove(random_choice)
                        direction_index = utils.DIRECTIONS.index(next_directions[random_choice])
                        increment = -1 if random_choice == 0 else 1
                        reached_edge, best_hex_river_edges = self.calc_hex_river(tile, direction_index, increment)
                    self.set_hex_river(tile, best_hex_river_edges)
                    return i
            if next_directions == None:
                branch = [0, 1, 2, 3, 4, 5] # River entering new tile will have 2 options to branch to
                best_hex_river_edges = []
                continue_next_tile = False
                while(len(branch) > 0) and not continue_next_tile:
                    print("3")
                    direction_index = random.choice(branch)
                    branch.remove(direction_index)
                    increment_list = [-1, 1]
                    for increment in increment_list:
                        continue_next_tile, best_hex_river_edges = self.calc_hex_river(tile, direction_index, increment, next_tile_direction)
                        if continue_next_tile:
                            break
                self.set_hex_river(tile, best_hex_river_edges)
                print(best_hex_river_edges)
                if continue_next_tile:
                    next_directions = utils.RIVER_TILE_MAPPINGS[(next_tile_direction, best_hex_river_edges[-1])]
                else:
                    return i

            else:
                branch = [0, 1] # River entering new tile will have 2 options to branch to
                best_hex_river_edges = []
                continue_next_tile = False
                while(len(branch) > 0) and not continue_next_tile:
                    print("4")
                    random_choice = random.choice(branch)
                    branch.remove(random_choice)
                    direction_index = utils.DIRECTIONS.index(next_directions[random_choice])
                    increment = -1 if random_choice == 0 else 1
                    continue_next_tile, best_hex_river_edges = self.calc_hex_river(tile, direction_index, increment, next_tile_direction)
                self.set_hex_river(tile, best_hex_river_edges)
                if continue_next_tile:
                    next_directions = utils.RIVER_TILE_MAPPINGS[(next_tile_direction, best_hex_river_edges[-1])]
                else:
                    return i
                
                

            
            

            

        
    def calc_hex_river(self, tile, direction_index, increment, next_tile_direction = None):
        if next_tile_direction != None:
            hex_river_edges = []
            reached_next_tile = True
            hex_river_edges.append(utils.DIRECTIONS[direction_index])

            # Loop around hex until river can reach next tile
            while utils.RIVER_TILE_MAPPINGS.get((next_tile_direction, utils.DIRECTIONS[direction_index]), None) == None:
                if tile.rivers[utils.DIRECTIONS[direction_index]] == True:
                    reached_next_tile = False
                    break
                direction_index += increment
                if direction_index == -1:
                    direction_index = 5
                elif direction_index == 6:
                    direction_index = 0
                hex_river_edges.append(utils.DIRECTIONS[direction_index])
            
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
            print(out_of_bound_tile_directions)
            while reached_edge == False:
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
        print(scale)
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



# Perlin Noise
# Terrain: Separate Perlin Noise
# Feature: Separate Perlin Noise
# River: Pathfinding from edge to edge with random branches? Perhaps take into account terrain or lowest terrain?
# Biome: Separate Perlin Noise
# Ensure all traversible tiles are reachable to one another
    # If tile is not reachable
