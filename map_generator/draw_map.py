import pygame
import math
import map_generator.config as config

def axial_to_pixel(q, r, radius, map_pixel_height):
    width = math.sqrt(3) * radius
    height = 2 * radius
    
    x_offset = width / 2       
    y_offset = radius          
    
    x = width * (q + r/2) + x_offset
    y = height * (3/4) * r + y_offset
    
    y = map_pixel_height - y - 1
    
    return (x, y)


def calc_hex_corners(center_x, center_y, radius):
    corners = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        corners.append((x, y))
    return corners


def draw_tiles(screen, width, height, map = None):
    hex_radius = config.hex["radius"]
    offsetX = config.map_settings["offsetX"]
    offsetY = config.map_settings["offsetY"]
    for column in range(width):
        x, y = axial_to_pixel(column, 0, hex_radius, height)
        corners = calc_hex_corners(x, y, hex_radius)

        pygame.draw.polygon(screen, (100, 200, 100), corners, 0)
        pygame.draw.polygon(screen, (0, 0, 0), corners, 2)