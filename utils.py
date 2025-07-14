import math
import config as config
import pygame

def click_to_hex(pos_x, pos_y):
    pos_x -= config.map_settings["offsetX"] - config.hex["inner_radius"]
    pos_y -= config.map_settings["offsetY"] - config.hex["radius"]
    pos_y = config.map_settings["pixel_height"] - pos_y - 1
    x = pos_x / (config.hex["inner_radius"] * 2) - 1 
    y = -x
    offset = pos_y / (config.hex["radius"] * 3)
    x -= offset
    y -= offset
    z = -x - y
   
    
    iX = round(x)
    iY = round(y)
    iZ = round(z)
    if iX + iY + iZ != 0:
        dX = abs(x - iX)
        dY = abs(y - iY)
        dZ = abs(-x -y - iZ)
        if dX > dY and dX > dZ:
            iX = -iY - iZ
            
        elif (dZ > dY):
            iZ = -iX - iY
        elif (dY > dX and dY > dZ):
            iY = -iX - iZ
        else:
            iX = -iY - iZ
    return (iX, iY, iZ)

def pos_to_edge(x, y, z, org_edge = None, ll = None):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    center_x, center_y = coord_to_pixel(*hex_coord_to_coord(x, y, z))

    dx = mouse_x - center_x
    dy = center_y - mouse_y
    distance = math.sqrt(dx ** 2 + dy ** 2)
    if distance < .25 * config.hex["radius"]:
        return None
    angle = math.degrees(math.atan2(dy, dx)) % 360

    direction_ranges = {
        "E":  (330, 30),
        "NE": (30, 90),
        "NW": (90, 150),
        "W":  (150, 210),
        "SW": (210, 270),
        "SE": (270, 330),
    }

    for direction, (start, end) in direction_ranges.items():
        if start < end:
            if start <= angle < end:
                closest = direction
                break
        else:  # Wraparound case (e.g., E)
            if angle >= start or angle < end:
                closest = direction
                break
    else:
        return None

    return closest

def coord_to_pixel(q, r):
    radius = config.hex["radius"]
    offsetX = config.map_settings["offsetX"]
    offsetY = config.map_settings["offsetY"]
    map_pixel_height = config.map_settings["pixel_height"]
    width = math.sqrt(3) * radius
    height = 2 * radius
    
    x_offset = width / 2       
    y_offset = radius          
    
    x = width * (q + (r/2 % 1)) + x_offset
    y = height * (3/4) * r + y_offset
    
    y = map_pixel_height - y - 1
    x += offsetX
    y += offsetY
    return (x, y)

def coord_to_hex_coord(row, column):
    x = column - int(row / 2)
    y = -x - row
    z = row
    return (x, y, z)
    
def hex_coord_to_coord(x, y, z):
    row = z
    column = x + int(row / 2)
    return (column, row)

def get_tile_via_edge(x, y, z, edge):
    return tuple(a + b for a, b in zip((x, y, z), CUBE_DIRECTIONS_DICT[edge]))

def get_relative_position(first_coord, second_coord):
    for x in CUBE_DIRECTIONS_DICT.keys():
        if tuple(a + b for a, b in zip(first_coord, CUBE_DIRECTIONS_DICT[x])) == second_coord:
            return x
    return None

CUBE_DIRECTIONS = [
    (+1, -1, 0),   # direction 0
    (+1, 0, -1),   # direction 1
    (0, +1, -1),   # direction 2
    (-1, +1, 0),   # direction 3
    (-1, 0, +1),   # direction 4
    (0, -1, +1)    # direction 5
]

CUBE_DIRECTIONS_DICT = {
    "E":  CUBE_DIRECTIONS[0],  # 0°
    "SE": CUBE_DIRECTIONS[1],  # 60°
    "SW": CUBE_DIRECTIONS[2],  # 120°
    "W":  CUBE_DIRECTIONS[3],  # 180°
    "NW": CUBE_DIRECTIONS[4],  # 240°
    "NE": CUBE_DIRECTIONS[5],  # 300°
}


OPPOSITE_EDGES = {
    "E": "W",
    "NE": "SW",
    "NW": "SE",
    "W": "E",
    "SW": "NE",
    "SE": "NW"
}


def get_health_color(health):
    if health > 90:
        hp_color = (0, 120, 32)
    elif health > 75:
        hp_color = (0, 219, 58)
    elif health > 50:
        hp_color = (227, 208, 5)
    elif health > 25:
        hp_color = (217, 125, 4)
    elif health > 0:
        hp_color = (240, 54, 2)
    else:
        hp_color = (46, 11, 1)
        
    return hp_color

def blit_text_border(screen, text, pos, border_width, font, color = (0, 0, 0)):
    
    label_surf = font.render(str(text), True, color)

    screen.blit(label_surf, (pos[0] + border_width, pos[1] + border_width))
    screen.blit(label_surf, (pos[0] + border_width, pos[1] - border_width))
    screen.blit(label_surf, (pos[0] - border_width, pos[1] + border_width))
    screen.blit(label_surf, (pos[0] - border_width, pos[1] - border_width))
    
def combat_strength_color(unit_1_CS, unit_2_CS):
    if unit_1_CS - unit_2_CS >= 4:
        return ((0, 120, 32), (240, 54, 2))
    elif unit_1_CS - unit_2_CS >= 2:
        return ((0, 219, 58), (217, 125, 4)) 
    elif unit_1_CS - unit_2_CS > -2:
        return ((227, 208, 5), (227, 208, 5))
    elif unit_1_CS - unit_2_CS > -4:
        return ((217, 125, 4), (0, 219, 58)) 
    else:
        return ((240, 54, 2), (0, 120, 32))  

def move_screen_to_tile(tile, screen):
    pixel_height = config.map_settings["pixel_height"]
    
    center_x, center_y = coord_to_pixel(*hex_coord_to_coord(tile.x, tile.y, tile.z))
    
    config.map_settings["offsetX"] -= center_x - (screen.get_width() / 2)
    config.map_settings["offsetY"] -= center_y - (pixel_height / 2)
    config.map_change = True