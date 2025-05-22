import math
import pygame
import interactions.utils as utils
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
        
    def get_coords(self):
        return (self.x, self.y, self.z)

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
    
