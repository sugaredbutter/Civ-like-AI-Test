import pygame
import math
import random
import interactions.config as config
import interactions.utils as utils
import map_generator.tile_types_config as tile_types_config
class Map:
    def __init__(self, screen):
        self.screen = screen
        
    def axial_to_pixel(self, q, r, radius, map_pixel_height):
        width = math.sqrt(3) * radius
        height = 2 * radius
        
        x_offset = width / 2       
        y_offset = radius          
        
        x = width * (q + (r/2 % 1)) + x_offset
        y = height * (3/4) * r + y_offset
        
        y = map_pixel_height - y - 1
        
        return (x, y)


    def calc_hex_corners(self, center_x, center_y, radius):
        corners = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            corners.append((x, y))
        return corners


    def draw_tiles(self, width, height, map = None):
        hex_radius = config.hex["radius"]
        offsetX = config.map_settings["offsetX"]
        offsetY = config.map_settings["offsetY"]
        mouse_x, mouse_y = pygame.mouse.get_pos()
        q, r, s = utils.click_to_hex(mouse_x, mouse_y)
        for column in range(map.width):
            for row in range(map.height):
                x, y= self.axial_to_pixel(column, row, hex_radius, height)
                x += offsetX
                y += offsetY
                corners = self.calc_hex_corners(x, y, hex_radius)
                tile = map.get_tile(row, column)
                if tile.get_coords() == (q, r, s):
                    self.draw_hex(corners, tile, True)
                else:
                    self.draw_hex(corners, tile)
                
                self.place_coords((x, y), tile)
                
    def draw_hex(self, corners, tile, hover = False):
        if hover:
            pygame.draw.polygon(self.screen, tile_types_config.biomes[tile.biome]["hover_color"], corners, 0)
        else:
            pygame.draw.polygon(self.screen, tile_types_config.biomes[tile.biome]["biome_color"], corners, 0)
        pygame.draw.polygon(self.screen, (0, 0, 0), corners, 2)
            
    def draw_hill(self, center, corners, tile, num_hills, hover = False):
        rng = random.Random((tile.x, tile.y, tile.z))
        radius = config.hex["radius"]
        hills_list = []
        min_x = corners[3][0]
        min_y = corners[3][1]
        max_x = corners[0][0] - radius/2
        max_y = corners[0][1]

        for i in range(num_hills):
            left_corner = (rng.random(0, 0.5), rng.random(0, 1))
            right_corner = (rng.random(left_corner[0] + .2, 1), left_corner[1])
            top = (right_corner[0] - left_corner[0], rng.random(left_corner[1] + .2, 1))
            
        if hover:
            pygame.draw.arc(self.screen, tile_types_config.terrain[tile.terrain]["hover_color"], rect, 0, math.pi, 2)
        else:
            pygame.draw.arc(self.screen, tile_types_config.terrain[tile.terrain]["terrain_color"], rect, 0, math.pi, 2)

    def place_coords(self, center, tile):
        font = pygame.font.SysFont(None, 24)  
        label = font.render(f"{tile.x},{tile.y},{tile.z}", True, (0, 0, 0))  

        label_rect = label.get_rect(center=center)

        self.screen.blit(label, label_rect)
