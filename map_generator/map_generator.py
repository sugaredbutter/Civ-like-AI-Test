import math
import pygame
import interactions.utils as utils
import random
class Tile:
    def __init__(self, x, y, z, biome = "Plain", terrain = "Flat", vegetation = "none"):
        self.x = x
        self.y = y
        self.z = z
        self.biome = biome
        self.terrain = terrain
        self.vegetation = vegetation
        self.movement = 1
        self.defense = 0
        self.offense = 0
        self.hills_list = []
        self.init_hill()
        
    def get_coords(self):
        return (self.x, self.y, self.z)

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

class HexMap:
    def __init__(self, width, height):
        self.tiles = {}
        self.width = width
        self.height = height
        for row in range(height): 
            for column in range(width):     
                print("Orig", row, column) 
                x, y, z = utils.coord_to_hex_coord(row, column)
                self.tiles[(x, y, z)] = Tile(x, y, z)
                print(x, y, z)

    def get_tile(self, row, column):
        x = column - int(row / 2)
        y = -x - row
        z = row
        return self.tiles.get((x, y, z), None)
    
