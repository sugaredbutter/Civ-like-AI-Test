import pygame
import math
import interactions.config as config
import interactions.utils as utils

def axial_to_pixel(q, r, radius, map_pixel_height):
    width = math.sqrt(3) * radius
    height = 2 * radius
    
    x_offset = width / 2       
    y_offset = radius          
    
    x = width * (q + (r/2 % 1)) + x_offset
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
    mouse_x, mouse_y = pygame.mouse.get_pos()
    q, r, s = utils.click_to_hex(mouse_x, mouse_y)
    for column in range(map.width):
        for row in range(map.height):
            x, y= axial_to_pixel(column, row, hex_radius, height)
            x += offsetX
            y += offsetY
            corners = calc_hex_corners(x, y, hex_radius)
            if map.get_tile(row, column).get_coords() == (q, r, s):
                draw_hex(screen, corners, map.get_tile(row, column), True)
            else:
                draw_hex(screen, corners, map.get_tile(row, column))
            place_coords(screen, (x, y), map.get_tile(row, column))
            
def draw_hex(screen, corners, tile, hover = False):
    if hover:
        pygame.draw.polygon(screen, (150, 255, 150), corners, 0)  # lighter green
        pygame.draw.polygon(screen, (0, 0, 0), corners, 2)
    else:
        pygame.draw.polygon(screen, (100, 200, 100), corners, 0)  # normal green
        pygame.draw.polygon(screen, (0, 0, 0), corners, 2)
        
def place_coords(screen, center, tile):
    font = pygame.font.SysFont(None, 24)  # Or use pygame.font.Font("path_to_ttf", size)
    label = font.render(f"{tile.x},{tile.y},{tile.z}", True, (0, 0, 0))  # Black text

    # Center text (optional)
    label_rect = label.get_rect(center=center)

    # Draw it
    screen.blit(label, label_rect)
