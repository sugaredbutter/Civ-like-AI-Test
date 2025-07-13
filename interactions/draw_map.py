import pygame
import math
import random
import config as config
import interactions.utils as utils
import map_generator.tile_types_config as tile_types_config
class Map:
    def __init__(self, screen, map, players, units, game_manager):
        self.screen = screen
        self.map = map
        self.players = players
        self.units = units
        self.game_manager = game_manager

        self.tree_1 = pygame.image.load("Assets/Trees/Tree_1.png")
        self.plains_hex = pygame.image.load("Assets/Trees/hex_template.png")
        self.red_melee = pygame.image.load("Assets/Units/Red/red_melee.png")
        self.red_archer = pygame.image.load("Assets/Units/Red/red_archer.png")
        self.red_cavalry = pygame.image.load("Assets/Units/Red/red_cavalry.png")

        self.saved_info = {}
        self.calculate_corners()
        
    def axial_to_pixel(self, q, r, radius, map_pixel_height):
        offsetX = config.map_settings["offsetX"]
        offsetY = config.map_settings["offsetY"]
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


    def calc_hex_corners(self, center_x, center_y, radius):
        corners = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            corners.append((x, y))
        return corners

    def calculate_corners(self):
        hex_radius = config.hex["radius"]
        width, height = config.map_settings["pixel_width"], config.map_settings["pixel_height"]


        for column in range(self.map.width):
            for row in range(self.map.height):
                x, y = self.axial_to_pixel(column, row, hex_radius, height)
                corners = self.calc_hex_corners(x, y, hex_radius)
                self.saved_info[(row, column)] = (corners, (x,y))
              
    def draw_tiles(self, width, height):
        if config.map_change == True:
            self.calculate_corners()
            config.map_change = False
        current_player = self.players.get_player(self.game_manager.current_player)
        self.border_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        self.border_surface.fill((0, 0, 0, 0))  # fully transparent

        self.fog_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.attackable_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        hex_radius = config.hex["radius"]
        mouse_x, mouse_y = pygame.mouse.get_pos()
        q, r, s = utils.click_to_hex(mouse_x, mouse_y)

        
        # Draw hexagons
        for column in range(self.map.width):
            for row in range(self.map.height):
                info = self.saved_info[(row, column)]
                corners = info[0]
                x, y = info[1]
                tile = self.map.get_tile(row, column)
                if config.game_type != None and tile.get_coords() not in current_player.revealed_tiles:
                    continue
                elif tile.get_coords() == (q, r, s):
                    self.draw_hex(corners, tile, True)
                else:
                    self.draw_hex(corners, tile)
              

        # Draw Rivers
        for column in range(self.map.width):
            for row in range(self.map.height):
                
                info = self.saved_info[(row, column)]
                corners = info[0]
                x, y = info[1]
                tile = self.map.get_tile(row, column)
                if config.game_type != None and tile.get_coords() not in current_player.revealed_tiles:
                    continue
                self.draw_rivers(corners, tile)
        # Draw terrain 
    
        for row in range(self.map.height - 1, -1, -1):
            for column in range(self.map.width):
                info = self.saved_info[(row, column)]
                corners = info[0]
                x, y = info[1]
                tile = self.map.get_tile(row, column)
                if config.game_type != None and tile.get_coords() not in current_player.revealed_tiles:
                    continue
                if tile.terrain == "Hill":
                    if tile.get_coords() == (q, r, s):
                        self.draw_hill(corners, tile, True)
                    else:
                        self.draw_hill(corners, tile)
                elif tile.terrain == "Mountain":
                    if tile.get_coords() == (q, r, s):
                        self.draw_mountain(corners, tile, True)
                    else:
                        self.draw_mountain(corners, tile)
                if tile.feature == "Forest":
                    self.draw_forest(corners, tile)

        
    

        #Movement
        for column in range(self.map.width):
            for row in range(self.map.height):
                info = self.saved_info[(row, column)]
                corners = info[0]
                x, y = info[1]
                tile = self.map.get_tile(row, column)
                if tile.path:
                    self.draw_movement(tile)
        
        for column in range(self.map.width):
            for row in range(self.map.height):
                info = self.saved_info[(row, column)]
                corners = info[0]
                x, y = info[1]
                tile = self.map.get_tile(row, column)
                #if config.game_type != None and tile.get_coords() in current_player.visible_tiles:
                self.place_coords((x, y + hex_radius/2), tile)
        
        if self.map.selected_edge is not None and self.map.hovered_tile is not None:
            column, row = utils.hex_coord_to_coord(self.map.hovered_tile.x, self.map.hovered_tile.y, self.map.hovered_tile.z)
            info = self.saved_info[(row, column)]
            corners = info[0]
            edge_color = (245, 66, 212)
            if self.map.selected_edge == "E":
                pygame.draw.line(self.screen, edge_color, corners[0], corners[1], width=10)
            if self.map.selected_edge == "SE":
                pygame.draw.line(self.screen, edge_color, corners[1], corners[2], width=10)
            if self.map.selected_edge == "SW":
                pygame.draw.line(self.screen, edge_color, corners[2], corners[3], width=10)
            if self.map.selected_edge == "W":
                pygame.draw.line(self.screen, edge_color, corners[3], corners[4], width=10)
            if self.map.selected_edge == "NW":
                pygame.draw.line(self.screen, edge_color, corners[4], corners[5], width=10)
            if self.map.selected_edge == "NE":
                pygame.draw.line(self.screen, edge_color, corners[5], corners[0], width=10)
        
        
        # Draw Units
        bar_width = config.health_bar["width_ratio"] * hex_radius
        bar_height = config.health_bar["height_ratio"] * hex_radius
        for column in range(self.map.width):
            for row in range(self.map.height):
                tile = self.map.get_tile(row, column)
                if config.game_type != None and tile.get_coords() not in current_player.visible_tiles:
                    continue
                if tile.unit_id != None:
                    x, y = self.axial_to_pixel(column, row, hex_radius, height)
                    bar_x = x - bar_width / 2
                    bar_y = y + bar_height / 2 + hex_radius * .25
                    unit = self.units.get_unit(tile.unit_id)
                    #pygame.draw.circle(self.screen, self.players.get_player(unit.owner_id).color, (int(x), int(y)), hex_radius/10)
                    
                    icon_size = int(hex_radius) * 1.1

                    if unit.type == "Melee":
                        unit_icon = pygame.transform.scale(self.red_melee, (icon_size, icon_size))
                    elif unit.type == "Ranged":
                        unit_icon = pygame.transform.scale(self.red_archer, (icon_size, icon_size))
                    elif unit.type == "Cavalry":
                        unit_icon = pygame.transform.scale(self.red_cavalry, (icon_size, icon_size))
                    self.screen.blit(unit_icon, (x - icon_size // 2, y - icon_size // 2 - hex_radius * .3))

                    # Unit Health bar
                    pygame.draw.rect(self.screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
                    # Foreground (green) - scaled width
                    pygame.draw.rect(self.screen, (0, 255, 0), (bar_x, bar_y, bar_width * unit.health/100, bar_height))
                    # Optional border
                    pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)
        hovered_tile = self.map.selected_tile
        if hovered_tile is not None:
            r, q = utils.hex_coord_to_coord(hovered_tile.x, hovered_tile.y, hovered_tile.z)
            x, y = self.axial_to_pixel(r, q, hex_radius, height)
            pygame.draw.circle(self.screen, (255, 0, 0), (int(x), int(y)), hex_radius/1.2, width=2)

        for column in range(self.map.width - 1, -1, -1):
            for row in range(self.map.height - 1, -1, -1):
                info = self.saved_info[(row, column)]
                corners = info[0]
                x, y = info[1]
                tile = self.map.get_tile(row, column)
                if config.game_type != None and tile.get_coords() not in current_player.revealed_tiles:
                    continue
                if config.game_type != None and tile.get_coords() not in current_player.visible_tiles:
                    pygame.draw.polygon(self.fog_surface, (0, 0, 0, 100), corners)
                elif config.game_type != None and tile.attackable == True:
                    pygame.draw.polygon(self.attackable_surface, (255, 34, 18, 100), corners)

        self.screen.blit(self.border_surface, (0, 0))
        self.screen.blit(self.fog_surface, (0, 0))
        self.screen.blit(self.attackable_surface, (0, 0))
        #self.screen.blit(self.plains_hex, (0, 0))
    def draw_hex(self, corners, tile, hover = False):
        #if tile.path:
        #    pygame.draw.polygon(self.screen, (100, 100, 100), corners, 0)
        if hover:
            pygame.draw.polygon(self.screen, tile_types_config.biomes[tile.biome]["hover_color"], corners, 0)
        else:
            pygame.draw.polygon(self.screen, tile_types_config.biomes[tile.biome]["biome_color"], corners, 0)
        pygame.draw.polygon(self.border_surface, (0, 0, 0, 100), corners, width=2)
        
    def draw_mountain(self, corners, tile, hover = False):
        radius = config.hex["radius"]
        min_x = corners[3][0]
        min_y = (corners[2][1] + corners[3][1]) / 2
        max_x = corners[0][0]
        max_y = corners[0][1]

        for i in tile.mountains_list:
            left_corner = (min_x + (max_x - min_x) * i[0][0], min_y + (max_y - min_y) * i[0][1])
            right_corner = (min_x + (max_x - min_x) * i[1][0], min_y + (max_y - min_y) * i[1][1])
            top = (min_x + (max_x - min_x) * i[2][0], min_y + (max_y - min_y) * i[2][1])
            if hover:
                pygame.draw.polygon(self.screen, tile_types_config.biomes[tile.biome]["Terrain"][tile.terrain]["hover_color"], [left_corner, right_corner, top])
                pygame.draw.polygon(self.screen, (0, 0, 0), [left_corner, right_corner, top], width=1)
            else:
                pygame.draw.polygon(self.screen, tile_types_config.biomes[tile.biome]["Terrain"][tile.terrain]["terrain_color"], [left_corner, right_corner, top])
                pygame.draw.polygon(self.screen, (0, 0, 0), [left_corner, right_corner, top], width=1)
            
    
    def draw_hill(self, corners, tile, hover = False):
        radius = config.hex["radius"]
        min_x = corners[3][0]
        min_y = (corners[2][1] + corners[3][1]) / 2
        max_x = corners[0][0]
        max_y = corners[0][1]

        for i in tile.hills_list:
            left_corner = (min_x + (max_x - min_x) * i[0][0], min_y + (max_y - min_y) * i[0][1])
            right_corner = (min_x + (max_x - min_x) * i[1][0], min_y + (max_y - min_y) * i[1][1])
            top = (min_x + (max_x - min_x) * i[2][0], min_y + (max_y - min_y) * i[2][1])
            if hover:
                pygame.draw.polygon(self.screen, tile_types_config.biomes[tile.biome]["Terrain"][tile.terrain]["hover_color"], [left_corner, right_corner, top])
                pygame.draw.polygon(self.screen, (0, 0, 0), [left_corner, right_corner, top], width=1)
            else:
                pygame.draw.polygon(self.screen, tile_types_config.biomes[tile.biome]["Terrain"][tile.terrain]["terrain_color"], [left_corner, right_corner, top])
                pygame.draw.polygon(self.screen, (0, 0, 0), [left_corner, right_corner, top], width=1)
            
        #if hover:
        #    pygame.draw.arc(self.screen, tile_types_config.terrain[tile.terrain]["hover_color"], rect, 0, math.pi, 2)
        #else:
        #    pygame.draw.arc(self.screen, tile_types_config.terrain[tile.terrain]["terrain_color"], rect, 0, math.pi, 2)

    def draw_forest(self, corners, tile, hover = False):
        radius = config.hex["radius"]
        min_x = corners[3][0]
        min_y = (corners[2][1] + corners[3][1]) / 2
        max_x = corners[0][0]
        max_y = corners[0][1]
        count = 0
        for i in tile.tree_list:
            if tile.terrain != "Hill" or count % 3 == 0:
                tree_point = (min_x + (max_x - min_x) * i[0], min_y + (max_y - min_y) * i[1])
                tree_width = int(config.hex["radius"] * .75)
                tree_height = int(config.hex["radius"] * .75)
                scaled_tree = pygame.transform.scale(self.tree_1, (tree_width, tree_height))

                x = tree_point[0] - tree_width // 2
                y = tree_point[1] - tree_height

                self.screen.blit(scaled_tree, (x, y))
            count += 1
    
    def draw_rivers(self, corners, tile):
        edge_color = (30, 43, 230)
        if tile.rivers["E"] == True:
            pygame.draw.line(self.screen, edge_color, corners[0], corners[1], width=10)
        if tile.rivers["SE"] == True:
            pygame.draw.line(self.screen, edge_color, corners[1], corners[2], width=10)
        if tile.rivers["SW"] == True:
            pygame.draw.line(self.screen, edge_color, corners[2], corners[3], width=10)
        if tile.rivers["W"] == True:
            pygame.draw.line(self.screen, edge_color, corners[3], corners[4], width=10)
        if tile.rivers["NW"] == True:
            pygame.draw.line(self.screen, edge_color, corners[4], corners[5], width=10)
        if tile.rivers["NE"] == True:
            pygame.draw.line(self.screen, edge_color, corners[5], corners[0], width=10)
            
    def draw_movement(self, tile):
        tile_x, tile_y = utils.hex_coord_to_coord(tile.x, tile.y, tile.z)
        tile_pixel = self.axial_to_pixel(tile_x, tile_y, config.hex["radius"], self.screen.get_height())
        if tile.neighbor is not None:
            neighbor_tile = tile.neighbor
            neighbor_tile_x, neighbor_tile_y = utils.hex_coord_to_coord(neighbor_tile.x, neighbor_tile.y, neighbor_tile.z)
            neighbor_pixel = self.axial_to_pixel(neighbor_tile_x, neighbor_tile_y, config.hex["radius"], self.screen.get_height())
            
            pygame.draw.line(self.screen, (248, 0, 252), (tile_pixel), neighbor_pixel, 2)
        if tile.turn_reached != -1:
            font = pygame.font.SysFont(None, 48)  
            label = font.render(f"{tile.turn_reached}", True, (0, 0, 0))  

            label_rect = label.get_rect(center=tile_pixel)

            self.screen.blit(label, label_rect)
        return

    def place_coords(self, center, tile):
        font = pygame.font.SysFont(None, 24)  
        label = font.render(f"{tile.x},{tile.y},{tile.z}", True, (0, 0, 0))  

        label_rect = label.get_rect(center=center)

        self.screen.blit(label, label_rect)
