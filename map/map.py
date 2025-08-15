import math
import pygame
import utils as utils
import random
import map.tile_types_config as tile_types_config
import config as config
from generator.map_generator import MapGenerator
class Tile:
    def __init__(self, x, y, z, biome = "Plain", terrain = "Flat", feature = None):
        self.x = x
        self.y = y
        self.z = z
        self.biome = biome      
        self.terrain = terrain
        self.feature = feature      

        self.elevation = 0
        self.temperature = 0
        self.moisture = 0
        
        self.movement = 1
        self.defense = 0
        self.offense = 0
        self.unit_id = None
        
        self.path = False
        self.neighbor = None
        self.turn_reached = -1
        
        self.attackable = False
        
        self.hills_list = []
        self.init_hill()
        self.mountains_list = []
        self.init_mountains()
        self.tree_list = []
        self.init_trees()
        
        self.rivers = {
            "W": False,
            "NW": False,
            "NE": False,
            "E": False,
            "SE": False,
            "SW": False
        }
        
        
    def get_coords(self):
        return (self.x, self.y, self.z)
    
    def get_axial_coords(self):
        return utils.hex_coord_to_coord(self.x, self.y, self.z)
    
    def set_biome(self, biome):
        if biome == "Desert":
            if self.feature == "Forest":
                self.feature = None
        self.biome = biome
    
    def set_terrain(self, terrain):
        if terrain == "Mountain":
            if self.feature == "Forest":
                self.feature = None
    
        self.terrain = terrain
        self.set_movement()
                
    def set_feature(self, feature, add):
        if add:
            if feature == "Forest":
                if self.biome == "Plain":
                    if self.terrain in ("Flat", "Hill"):
                        self.feature = feature
        elif add == False and self.feature == feature:
            self.feature = None

        self.set_movement()
        pass
    
    def set_movement(self):
        self.movement = tile_types_config.biomes[self.biome]["Terrain"][self.terrain]["movement"]
        if self.feature != None:
            self.movement += tile_types_config.biomes[self.biome]["Feature"][self.feature]["movement"]
        if self.movement == 0:
            self.movement = 1
    
    def get_movement(self, direction = None):
        movement = self.movement
        if direction == None or movement == -1:
            return movement
        if self.rivers[direction] == True:
            return movement + tile_types_config.features["River"]["movement"]
        return movement

    def init_hill(self, num_hills = -1):
        rng = random.Random(f"{self.x},{self.y},{self.z}")
        if num_hills == -1:
            num_hills = rng.randint(4, 8)
        self.hills_list = []

        for i in range(num_hills - 1, -1, -1):
            left_corner = (rng.uniform(0, 0.6), rng.uniform(i/num_hills, (i+1)/num_hills))
            right_corner = (rng.uniform(left_corner[0] + .2, min(left_corner[0] + .6, 1)), left_corner[1])
            top = ((right_corner[0] + left_corner[0]) / 2, rng.uniform(left_corner[1] + (right_corner[0] - left_corner[0]) / 5, left_corner[1] + (right_corner[0] - left_corner[0]) / 2.5))
            self.hills_list.append((left_corner, right_corner, top))
    
    def init_mountains(self, num = -1):
        rng = random.Random(f"{self.x},{self.y},{self.z}")
        if num == -1:
            num = rng.randint(2, 4)
        self.mountains_list = []

        for i in range(num - 1, -1, -1):
            left_corner = (rng.uniform(0, 0.4), rng.uniform(i/num, (i+1)/num))
            right_corner = (rng.uniform(left_corner[0] + .4, min(left_corner[0] + .8, 1)), left_corner[1])
            top = ((right_corner[0] + left_corner[0]) / 2, rng.uniform(left_corner[1] + (right_corner[0] - left_corner[0]) / 1.1, left_corner[1] + (right_corner[0] - left_corner[0]) / .65))
            self.mountains_list.append((left_corner, right_corner, top))
    
    def init_trees(self, num = -1):
        rng = random.Random(f"{self.x},{self.y},{self.z}")
        if num == -1:
            num = rng.randint(12, 16)
        self.tree_list = []

        for i in range(num - 1, -1, -1):
            tree_point = (rng.uniform(0, 1), rng.uniform(i/num, (i+1)/num))
            self.tree_list.append(tree_point)
            
    def end_game_reset_tile(self):
        self.unit_id = None
        self.path = False
        self.neighbor = None

class HexMap:
    def __init__(self, width, height):
        self.tiles = {}
        self.width = width
        self.height = height
        self.selected_tile = None
        self.hovered_tile = None
        self.selected_edge = None
        for row in range(height): 
            for column in range(width):     
                x, y, z = utils.coord_to_hex_coord(row, column)
                self.tiles[(x, y, z)] = Tile(x, y, z)
        map_generator = MapGenerator()
        self.tiles = map_generator.generate_map(self.width, self.height)

    def place_river(self, x, y, z, edge, adding):
        tile = self.get_tile_hex(x, y, z)
        neighbor_coord = utils.get_tile_via_edge(x, y, z, edge)
        neighbor_tile = self.get_tile_hex(*neighbor_coord)
        tile.rivers[edge] = adding        
        if neighbor_tile == None:
            return
        neighbor_edge = utils.OPPOSITE_EDGES[edge]
        neighbor_tile.rivers[neighbor_edge] = adding

    def get_tile(self, row, column):
        x = column - int(row / 2)
        y = -x - row
        z = row
        return self.tiles.get((x, y, z), None)
    
    def get_tile_hex(self, x, y, z):
        return self.tiles.get((x, y, z), None)
    
    def end_game_reset(self):
        for tile in self.tiles.values():
            tile.end_game_reset_tile()
        self.selected_tile = None

    def start_game(self):
        self.selected_tile = None
        self.hovered_tile = None
        self.selected_edge = None

    def randomize_map(self, save = False):
        if save:
            pass
        else:
            map_generator = MapGenerator()
            self.tiles = map_generator.generate_map(self.width, self.height)


    
