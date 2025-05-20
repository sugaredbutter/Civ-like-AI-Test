import math
import pygame
class Tile:
    def __init__(self, x, y, z, biome = "plain", terrain = "flat"):
        self.x = x
        self.y = y
        self.z = z
        self.biome = biome
        self.terrain = terrain

class HexMap:
    def __init__(self, width, height):
        self.tiles = {}
        self.width = width
        self.height = height
        for row in range(height): 
            for column in range(width):    
                print("Orig", row, column) 
                x = row - int(column / 2)
                y = -x - column
                z = column
                self.tiles[(x, y, z)] = Tile(x, y, z)
                print(x, y, z)
    def get_tile(self, row, column):
        x = row - int(column / 2)
        y = -x - column
        z = column
        return self.tiles[(x, y, z)]
