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
        seed = map_generator_config.seed
        self.rng = random.Random(seed)
        q_elevation_offset = self.rng.randint(-10000, 10000)
        r_elevation_offset = self.rng.randint(-10000, 10000)
        q_temperature_offset = self.rng.randint(-10000, 10000)
        r_temperature_offset = self.rng.randint(-10000, 10000)
        q_moisture_offset = self.rng.randint(-10000, 10000)
        r_moisture_offset = self.rng.randint(-10000, 10000)
        tiles = {}
        for row in range(height): 
            for column in range(width):     
                x, y, z = utils.coord_to_hex_coord(row, column)
                tiles[(x, y, z)] = current_map.Tile(x, y, z)
                tiles[(x, y, z)].elevation = self.hex_elevation(column, row, q_elevation_offset, r_elevation_offset)
                tiles[(x, y, z)].temperature = self.hex_temperature(column, row, q_temperature_offset, r_temperature_offset)
                tiles[(x, y, z)].moisture = self.hex_moisture(column, row, q_moisture_offset, r_moisture_offset)
                self.calc_tile_attributes(tiles[(x, y, z)])
        return tiles

    def calc_tile_attributes(self, tile):
        if tile.elevation > 0:
            tile.terrain = "Hill"



    def hex_elevation(self, q, r, q_offset, r_offset):
        scale = map_generator_config.scale
        octaves = map_generator_config.octaves
        persistence = map_generator_config.persistence
        lacunarity = map_generator_config.lacunarity

        return noise.pnoise2(
            q * scale + q_offset, r * scale + r_offset,   
            octaves = octaves,
            persistence = persistence,
            lacunarity = lacunarity,
        )
    
    def hex_temperature(self, q, r, q_offset, r_offset):
        scale = map_generator_config.scale
        octaves = map_generator_config.octaves
        persistence = map_generator_config.persistence
        lacunarity = map_generator_config.lacunarity

        return noise.pnoise2(
            q * scale + q_offset, r * scale + r_offset,   
            octaves = octaves,
            persistence = persistence,
            lacunarity = lacunarity,
        )
    
    def hex_moisture(self, q, r, q_offset, r_offset):
        scale = map_generator_config.scale
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
