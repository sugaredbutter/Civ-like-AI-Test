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
        if tile.temperature >= temperature:
            tile.biome = "Plain"
        else:
            tile.biome = "Desert"

        moisture = (map_generator_config.MapConfig["moisture"]["current"] - map_generator_config.MapConfig["moisture"]["default"]) * map_generator_config.Feature["moisture"]["change"]
        print(moisture)
        tree_moisture = map_generator_config.Feature["forest"]["level"]
        tree_moisture -= moisture
        if tile.moisture > tree_moisture and tile.biome != "Desert" and tile.terrain != "Mountain":
            tile.feature = "Forest"




    def hex_elevation(self, q, r, q_offset, r_offset):
        scale = map_generator_config.scale
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
