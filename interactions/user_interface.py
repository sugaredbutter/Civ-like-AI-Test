import pygame
import config as config
import interactions.utils as utils
import interactions.controls as controls

WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
DARK_GRAY = (120, 120, 120)
BLACK = (0, 0, 0)
WIDTH = config.map_settings["pixel_width"]
HEIGHT = config.map_settings["pixel_height"]
ROWS, COLUMNS = config.map_settings["tile_height"], config.map_settings["tile_width"]
ZOOM_SCALE = config.map_settings["zoom"]

class UserInterface:
    def __init__(self, screen, generated_map, player_handler, unit_handler):
        self.screen = screen
        self.generated_map = generated_map
        self.player_handler = player_handler
        self.unit_handler = unit_handler
        
        self.initX = 0
        self.initY = 0
        self.clicked = False
        self.dragging = False
        self.clicked_button = False
        
        self.button_width = 100
        self.button_height = 40
        self.padding = 10
        self.valid_hover = True
        self.active_button = None
        self.active_menu = self
        
        self.tile_controls = controls.TileClickControls(screen, self, generated_map, player_handler, unit_handler)
                
        self.Menus = [PainterMenu(screen, self, self, generated_map, self.tile_controls), TerrainMenu(screen, self, self, generated_map, self.tile_controls, self.unit_handler, self.player_handler), FeatureMenu(screen, self, self, generated_map, self.tile_controls), UnitMenu(screen, self, self, self.generated_map, self.player_handler, self.unit_handler, self.tile_controls)]
        menus_list = ["Biomes", "Terrain", "Features", "Units"]
        self.button_menu = {}

        for i, name in enumerate(menus_list):
            x = WIDTH - self.button_width - self.padding
            y = self.padding + i * (self.button_height + self.padding)
            self.button_menu[name] = (pygame.Rect(x, y, self.button_width, self.button_height), self.Menus[i])
            
    def left_click(self, event):
        self.clicked = True
        if self.is_clicked():
            self.clicked_button = True
        self.set_init(event)
    
    def left_click_up(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if self.clicked_button and self.is_clicked():
            self.button_clicked()   

        self.dragging = False
        self.clicked = False
        self.clicked_button = False
        self.valid_hover = True
    
    def right_click(self, event):
        return
    
    def right_click_up(self, event):
        return
    
    def mouse_move(self, event):
        if self.clicked and not self.clicked_button:
            self.valid_hover = False
            self.move_map(event)
        if not self.clicked and self.active_button != None:
            self.tile_hover()
         
    def zoom(self, event):
        if event.y > 0 and config.hex["radius"] < config.hex["max_radius"]:
            config.hex["radius"] += 5
            config.hex["inner_radius"] = config.hex["radius"] * 0.866025404
            config.map_settings["offsetX"] -= ZOOM_SCALE * COLUMNS
            config.map_settings["offsetY"] += ZOOM_SCALE * ROWS
        elif event.y < 0 and config.hex["radius"] > config.hex["min_radius"]:
            config.hex["radius"] -= 5
            config.hex["inner_radius"] = config.hex["radius"] * 0.866025404
            config.map_settings["offsetX"] += ZOOM_SCALE * COLUMNS
            config.map_settings["offsetY"] -= ZOOM_SCALE * ROWS

    def move_map(self, event):
        if self.active_button != None:
            self.interaction()
        else:
            self.dragging = True
            config.map_settings["offsetX"] += event.pos[0] - self.initX
            config.map_settings["offsetY"] += event.pos[1] - self.initY
            self.initX = event.pos[0]
            self.initY = event.pos[1]

    def set_init(self, event):
        self.initX = event.pos[0]
        self.initY = event.pos[1]
         
    
    def create_menu(self):
        for key in self.button_menu.keys():
            self.draw_button(key, self.button_menu[key][0], self.active_button == key)
    
    def draw_button(self, text, rect, is_hovered):
        font = pygame.font.SysFont(None, 24)
        pygame.draw.rect(self.screen, DARK_GRAY if self.is_hovered(rect) or is_hovered else GRAY, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)  # Border
        text_surf = font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
    
    def is_hovered(self, rect):
        if not self.valid_hover:
            return False
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_x, mouse_y):
            return True
        return False
    
    def is_clicked(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for key in self.button_menu.keys():
            if self.button_menu[key][0].collidepoint(mouse_x, mouse_y):
                return True
        return False

    def button_clicked(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for key in self.button_menu.keys():
            if self.button_menu[key][0].collidepoint(mouse_x, mouse_y):
                if self.button_menu[key][1] != None:
                    self.active_menu = self.button_menu[key][1]
                else:
                    if self.active_button == key:
                        self.active_button = None
                    else:
                        self.active_button = key
                    
            
class PainterMenu:
    def __init__(self, screen, main_menu, parent_menu, generated_map, tile_controls):
        self.screen = screen
        self.main_menu = main_menu
        self.parent_menu = parent_menu
        self.generated_map = generated_map
        self.tile_controls = tile_controls
        
        self.initX = 0
        self.initY = 0
        self.clicked = False
        self.dragging = False
        self.clicked_button = False
        
        self.button_width = 100
        self.button_height = 40
        self.padding = 10
        self.valid_hover = True
        self.active_button = None
        buttons = ["Back", "Desert", "Plain"]
        self.button_menu = {}

        for i, name in enumerate(buttons):
            x = WIDTH - self.button_width - self.padding
            y = self.padding + i * (self.button_height + self.padding)
            self.button_menu[name] = pygame.Rect(x, y, self.button_width, self.button_height)
    
    def left_click(self, event):
        self.clicked = True
        if self.is_clicked():
            self.clicked_button = True
        self.set_init(event)
    
    def left_click_up(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if self.clicked_button:
            self.button_clicked()   
        elif self.active_button != None:
            self.interaction()

        self.dragging = False
        self.clicked = False
        self.clicked_button = False
        self.valid_hover = True
    
    def right_click(self, event):
        return
    
    def right_click_up(self, event):
        return
    
    def mouse_move(self, event):
        if self.clicked and not self.clicked_button:
            self.valid_hover = False
            self.move_map(event)
        if not self.clicked and self.active_button != None:
            self.tile_hover()
         
    def zoom(self, event):
        if event.y > 0 and config.hex["radius"] < config.hex["max_radius"]:
            config.hex["radius"] += 5
            config.hex["inner_radius"] = config.hex["radius"] * 0.866025404
            config.map_settings["offsetX"] -= ZOOM_SCALE * COLUMNS
            config.map_settings["offsetY"] += ZOOM_SCALE * ROWS
        elif event.y < 0 and config.hex["radius"] > config.hex["min_radius"]:
            config.hex["radius"] -= 5
            config.hex["inner_radius"] = config.hex["radius"] * 0.866025404
            config.map_settings["offsetX"] += ZOOM_SCALE * COLUMNS
            config.map_settings["offsetY"] -= ZOOM_SCALE * ROWS

    def move_map(self, event):
        if self.active_button != None:
            self.interaction()
        else:
            self.dragging = True
            config.map_settings["offsetX"] += event.pos[0] - self.initX
            config.map_settings["offsetY"] += event.pos[1] - self.initY
            self.initX = event.pos[0]
            self.initY = event.pos[1]

    def set_init(self, event):
        self.initX = event.pos[0]
        self.initY = event.pos[1]
    
    def create_menu(self):
        for key in self.button_menu.keys():
            self.draw_button(key, self.button_menu[key], self.active_button == key)

    def draw_button(self, text, rect, is_hovered):
        font = pygame.font.SysFont(None, 24)
        pygame.draw.rect(self.screen, DARK_GRAY if self.is_hovered(rect) or is_hovered else GRAY, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)  # Border
        text_surf = font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
    
    def is_hovered(self, rect):
        if not self.valid_hover:
            return False
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_x, mouse_y):
            return True
        return False
    
    def is_clicked(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for key in self.button_menu.keys():
            if self.button_menu[key].collidepoint(mouse_x, mouse_y):
                return True
        return False
    
    def tile_hover(self):
        pass

    def button_clicked(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for key in self.button_menu.keys():
            if self.button_menu[key].collidepoint(mouse_x, mouse_y):
                if key == "Back":
                    self.main_menu.active_menu = self.parent_menu
                    self.active_button = None
                elif self.active_button == key:
                    self.active_button = None
                else:
                    self.active_button = key

    def interaction(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x, y, z = utils.click_to_hex(mouse_x, mouse_y)
        column, row = utils.hex_coord_to_coord(x, y, z)
        tile = self.generated_map.get_tile(row, column)
        if tile != None:
            tile.biome = self.active_button
        return
    
class TerrainMenu:
    def __init__(self, screen, main_menu, parent_menu, generated_map, tile_controls, unit_handler, player_handler):
        self.screen = screen
        self.main_menu = main_menu
        self.parent_menu = parent_menu
        self.generated_map = generated_map
        self.tile_controls = tile_controls
        self.unit_handler = unit_handler
        self.player_handler = player_handler
        
        self.initX = 0
        self.initY = 0
        self.clicked = False
        self.dragging = False
        self.clicked_button = False
        
        self.button_width = 100
        self.button_height = 40
        self.padding = 10
        self.valid_hover = True
        self.active_button = None
        buttons = ["Back", "Flat", "Hill", "Mountain"]
        self.button_menu = {}

        for i, name in enumerate(buttons):
            x = WIDTH - self.button_width - self.padding
            y = self.padding + i * (self.button_height + self.padding)
            self.button_menu[name] = pygame.Rect(x, y, self.button_width, self.button_height)
            
    def left_click(self, event):
        self.clicked = True
        if self.is_clicked():
            self.clicked_button = True
        elif self.active_button != None:
            self.interaction()
        self.set_init(event)
    
    def left_click_up(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if self.clicked_button:
            self.button_clicked()   

        self.dragging = False
        self.clicked = False
        self.clicked_button = False
        self.valid_hover = True
    
    def right_click(self, event):
        return
    
    def right_click_up(self, event):
        return
    
    def mouse_move(self, event):
        if self.clicked and not self.clicked_button:
            self.valid_hover = False
            self.move_map(event)
        if not self.clicked and self.active_button != None:
            self.tile_hover()
         
    def zoom(self, event):
        if event.y > 0 and config.hex["radius"] < config.hex["max_radius"]:
            config.hex["radius"] += 5
            config.hex["inner_radius"] = config.hex["radius"] * 0.866025404
            config.map_settings["offsetX"] -= ZOOM_SCALE * COLUMNS
            config.map_settings["offsetY"] += ZOOM_SCALE * ROWS
        elif event.y < 0 and config.hex["radius"] > config.hex["min_radius"]:
            config.hex["radius"] -= 5
            config.hex["inner_radius"] = config.hex["radius"] * 0.866025404
            config.map_settings["offsetX"] += ZOOM_SCALE * COLUMNS
            config.map_settings["offsetY"] -= ZOOM_SCALE * ROWS

    def move_map(self, event):
        if self.active_button != None:
            self.interaction()
        else:
            self.dragging = True
            config.map_settings["offsetX"] += event.pos[0] - self.initX
            config.map_settings["offsetY"] += event.pos[1] - self.initY
            self.initX = event.pos[0]
            self.initY = event.pos[1]

    def set_init(self, event):
        self.initX = event.pos[0]
        self.initY = event.pos[1]
    
    def create_menu(self):
        for key in self.button_menu.keys():
            self.draw_button(key, self.button_menu[key], self.active_button == key)

    def draw_button(self, text, rect, is_hovered):
        font = pygame.font.SysFont(None, 24)
        pygame.draw.rect(self.screen, DARK_GRAY if self.is_hovered(rect) or is_hovered else GRAY, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)  # Border
        text_surf = font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
    
    def is_hovered(self, rect):
        if not self.valid_hover:
            return False
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_x, mouse_y):
            return True
        return False
    
    def is_clicked(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for key in self.button_menu.keys():
            if self.button_menu[key].collidepoint(mouse_x, mouse_y):
                return True
        return False

    def button_clicked(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for key in self.button_menu.keys():
            if self.button_menu[key].collidepoint(mouse_x, mouse_y):
                if key == "Back":
                    self.main_menu.active_menu = self.parent_menu
                    self.active_button = None
                elif self.active_button == key:
                    self.active_button = None
                else:
                    self.active_button = key

    def tile_hover(self):
        pass

    def interaction(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x, y, z = utils.click_to_hex(mouse_x, mouse_y)
        column, row = utils.hex_coord_to_coord(x, y, z)
        tile = self.generated_map.get_tile(row, column)
        if tile != None:
            tile.set_terrain(self.active_button)
            unit_id = tile.unit_id
            if unit_id != None and tile.terrain == "Mountain":
                unit = self.unit_handler.get_unit(unit_id)
                unit_owner = self.player_handler.get_player(unit.owner_id)
                unit_owner.remove_unit(unit_id)
        return
    
class FeatureMenu:
    def __init__(self, screen, main_menu, parent_menu, generated_map, tile_controls):
        self.screen = screen
        self.main_menu = main_menu
        self.parent_menu = parent_menu
        self.generated_map = generated_map
        self.tile_controls = tile_controls
        
        self.initX = 0
        self.initY = 0
        self.clicked = False
        self.dragging = False
        self.clicked_button = False
        
        self.active_tile = None
        self.active_edge = None
        
        self.adding = True
        
        self.button_width = 100
        self.button_height = 40
        self.padding = 10
        self.valid_hover = True
        self.active_button = None
        buttons = ["Back", "River", "Forest"]
        self.button_menu = {}

        for i, name in enumerate(buttons):
            x = WIDTH - self.button_width - self.padding
            y = self.padding + i * (self.button_height + self.padding)
            self.button_menu[name] = pygame.Rect(x, y, self.button_width, self.button_height)
            
    def left_click(self, event):
        self.clicked = True
        if self.is_clicked():
            self.clicked_button = True
        elif self.active_button != None:
            self.interaction()
        self.set_init(event)
    
    def left_click_up(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if self.clicked_button:
            self.button_clicked()   

        self.dragging = False
        self.clicked = False
        self.clicked_button = False
        self.valid_hover = True
        self.active_tile = None
        self.active_edge = None
    
    def right_click(self, event):
        return
    
    def right_click_up(self, event):
        return
    
    def mouse_move(self, event):
        if self.clicked and not self.clicked_button:
            self.valid_hover = False
            self.move_map(event)
        if not self.clicked and self.active_button != None:
            self.tile_hover()
         
    def zoom(self, event):
        if event.y > 0 and config.hex["radius"] < config.hex["max_radius"]:
            config.hex["radius"] += 5
            config.hex["inner_radius"] = config.hex["radius"] * 0.866025404
            config.map_settings["offsetX"] -= ZOOM_SCALE * COLUMNS
            config.map_settings["offsetY"] += ZOOM_SCALE * ROWS
        elif event.y < 0 and config.hex["radius"] > config.hex["min_radius"]:
            config.hex["radius"] -= 5
            config.hex["inner_radius"] = config.hex["radius"] * 0.866025404
            config.map_settings["offsetX"] += ZOOM_SCALE * COLUMNS
            config.map_settings["offsetY"] -= ZOOM_SCALE * ROWS

    def move_map(self, event):
        if self.active_button != None:
            self.dragging = True
            self.interaction()
        else:
            self.dragging = True
            config.map_settings["offsetX"] += event.pos[0] - self.initX
            config.map_settings["offsetY"] += event.pos[1] - self.initY
            self.initX = event.pos[0]
            self.initY = event.pos[1]

    def set_init(self, event):
        self.initX = event.pos[0]
        self.initY = event.pos[1]
    
    def create_menu(self):
        for key in self.button_menu.keys():
            self.draw_button(key, self.button_menu[key], self.active_button == key)

    def draw_button(self, text, rect, is_hovered):
        font = pygame.font.SysFont(None, 24)
        pygame.draw.rect(self.screen, DARK_GRAY if self.is_hovered(rect) or is_hovered else GRAY, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)  # Border
        text_surf = font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
    
    def is_hovered(self, rect):
        if not self.valid_hover:
            return False
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_x, mouse_y):
            return True
        return False
    
    def is_clicked(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for key in self.button_menu.keys():
            if self.button_menu[key].collidepoint(mouse_x, mouse_y):
                return True
        return False

    def button_clicked(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for key in self.button_menu.keys():
            if self.button_menu[key].collidepoint(mouse_x, mouse_y):
                if key == "Back":
                    self.main_menu.active_menu = self.parent_menu
                    self.active_button = None
                    self.generated_map.selected_edge = None
                    self.generated_map.hovered_tile = None

                elif self.active_button == key:
                    self.active_button = None
                    self.generated_map.selected_edge = None
                    self.generated_map.hovered_tile = None

                else:
                    self.active_button = key
                    self.generated_map.selected_edge = None
                    self.generated_map.hovered_tile = None


    def tile_hover(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x, y, z = utils.click_to_hex(mouse_x, mouse_y)
        column, row = utils.hex_coord_to_coord(x, y, z)
        tile = self.generated_map.get_tile(row, column)
        if tile != None:
            if self.active_button == "River":
                active_edge = utils.pos_to_edge(x, y, z)
                if active_edge is not None:
                    self.generated_map.selected_edge = active_edge
                    self.generated_map.hovered_tile = tile
                else:
                    self.generated_map.selected_edge = None
                    self.generated_map.hovered_tile = None
                


    def interaction(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x, y, z = utils.click_to_hex(mouse_x, mouse_y)
        column, row = utils.hex_coord_to_coord(x, y, z)
        tile = self.generated_map.get_tile(row, column)
        if tile != None:
            if self.active_button == "River":
                edge = utils.pos_to_edge(x, y, z)
                if edge != None:
                    if self.dragging == False:
                        self.adding = not tile.rivers[edge]
                    self.generated_map.selected_edge = edge
                    self.generated_map.hovered_tile = tile

                    self.generated_map.place_river(x, y, z, edge, self.adding)
                    self.active_tile = tile
                    self.active_edge = edge
            else:
                if self.dragging == False:
                    self.adding = False if tile.feature == "Forest" else True
                tile.set_feature(self.active_button, self.adding)
            
        return
    
class UnitMenu:
    def __init__(self, screen, main_menu, parent_menu, generated_map, player_handler, unit_handler, tile_controls):
        self.screen = screen
        self.main_menu = main_menu
        self.parent_menu = parent_menu
        self.generated_map = generated_map
        self.player_handler = player_handler
        self.unit_handler = unit_handler
        self.tile_controls = tile_controls
        
        self.initX = 0
        self.initY = 0
        self.clicked = False
        self.dragging = False
        self.clicked_button = False
        
        self.button_width = 100
        self.button_height = 40
        self.padding = 10
        self.valid_hover = True

        buttons = ["Back", "Melee", "Ranged", "Remove"]
        self.player_buttons = ["Player 1", "Player 2", "Player 3", "Player 4", "Player 5"] #player 5 used as place holder for removing player
        self.adjust_num_players = ["+", "-"]
        self.active_button = None
        self.active_player = self.player_buttons[0]

        self.button_menu = {}
        self.player_button_menu = {}
        self.adjust_num_players_menu = {}

        for i, name in enumerate(buttons):
            x = WIDTH - self.button_width - self.padding
            y = self.padding + i * (self.button_height + self.padding)
            self.button_menu[name] = pygame.Rect(x, y, self.button_width, self.button_height)
            
        for i, name in enumerate(self.player_buttons):
            x = self.padding + (i + 1) * (self.button_width + self.padding)
            y = self.padding
            self.player_button_menu[name] = pygame.Rect(x, y, self.button_width, self.button_height)
            
        self.adjust_num_players_menu[self.adjust_num_players[0]] =  self.player_button_menu["Player 3"]
    
    def left_click(self, event):
        self.clicked = True
        if self.is_clicked():
            self.clicked_button = True
        elif self.active_button != None:
            self.interaction()
        self.set_init(event)
    
    def left_click_up(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if self.clicked_button:
            self.button_clicked()   

        self.dragging = False
        self.clicked = False
        self.clicked_button = False
        self.valid_hover = True
    
    def right_click(self, event):
        return
    
    def right_click_up(self, event):
        return
    
    def mouse_move(self, event):
        if self.clicked and not self.clicked_button:
            self.valid_hover = False
            self.move_map(event)
        if not self.clicked and self.active_button != None:
            self.tile_hover()
         
    def zoom(self, event):
        if event.y > 0 and config.hex["radius"] < config.hex["max_radius"]:
            config.hex["radius"] += 5
            config.hex["inner_radius"] = config.hex["radius"] * 0.866025404
            config.map_settings["offsetX"] -= ZOOM_SCALE * COLUMNS
            config.map_settings["offsetY"] += ZOOM_SCALE * ROWS
        elif event.y < 0 and config.hex["radius"] > config.hex["min_radius"]:
            config.hex["radius"] -= 5
            config.hex["inner_radius"] = config.hex["radius"] * 0.866025404
            config.map_settings["offsetX"] += ZOOM_SCALE * COLUMNS
            config.map_settings["offsetY"] -= ZOOM_SCALE * ROWS

    def move_map(self, event):
        if self.active_button != None:
            self.interaction()
        else:
            self.dragging = True
            config.map_settings["offsetX"] += event.pos[0] - self.initX
            config.map_settings["offsetY"] += event.pos[1] - self.initY
            self.initX = event.pos[0]
            self.initY = event.pos[1]

    def set_init(self, event):
        self.initX = event.pos[0]
        self.initY = event.pos[1]
    
    def create_menu(self):
        for key in self.button_menu.keys():
            self.draw_button(key, self.button_menu[key], self.active_button == key)
        for i, key in enumerate(self.player_button_menu.keys()):
            if i >= config.num_players:
                break
            self.draw_button(key, self.player_button_menu[key], self.active_player == key)
        for key in self.adjust_num_players_menu.keys():
            self.draw_button(key, self.adjust_num_players_menu[key], False)
            

    def draw_button(self, text, rect, is_hovered):
        font = pygame.font.SysFont(None, 24)
        pygame.draw.rect(self.screen, DARK_GRAY if self.is_hovered(rect) or is_hovered else GRAY, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)  # Border
        text_surf = font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
    
    def is_hovered(self, rect):
        if not self.valid_hover:
            return False
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_x, mouse_y):
            return True
        return False
    
    def is_clicked(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for key in self.button_menu.keys():
            if self.button_menu[key].collidepoint(mouse_x, mouse_y):
                return True
        for i, key in enumerate(self.player_button_menu.keys()):
            if i >= config.num_players:
                break
            if self.player_button_menu[key].collidepoint(mouse_x, mouse_y):
                return True
        for key in self.adjust_num_players_menu.keys():
            if self.adjust_num_players_menu[key].collidepoint(mouse_x, mouse_y):
                return True
            
        return False

    def button_clicked(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for key in self.button_menu.keys():
            if self.button_menu[key].collidepoint(mouse_x, mouse_y):
                if key == "Back":
                    self.main_menu.active_menu = self.parent_menu
                    self.active_button = None
                    self.active_player = self.player_buttons[0]
                elif self.active_button == key:
                    self.active_button = None
                else:
                    self.active_button = key  
        for i, key in enumerate(self.player_button_menu.keys()):
            if i >= config.num_players:
                break
            if self.player_button_menu[key].collidepoint(mouse_x, mouse_y):
                if self.active_player != key:
                    self.active_player = key
        for key in self.adjust_num_players_menu.keys():
            if self.adjust_num_players_menu[key].collidepoint(mouse_x, mouse_y):
                if key == "+" and config.num_players < 4:
                    config.num_players += 1
                    self.player_handler.add_player()

                    if config.num_players == 4:
                        del self.adjust_num_players_menu["+"]
                        self.adjust_num_players_menu["-"] = self.player_button_menu["Player 5"]
                    else:
                        self.adjust_num_players_menu["+"] = self.player_button_menu["Player " + str(config.num_players + 1)]
                        self.adjust_num_players_menu["-"] = self.player_button_menu["Player " + str(config.num_players + 2)]

                elif key == "-" and config.num_players > 2:
                    config.num_players -= 1
                    self.player_handler.remove_player()
                    if config.num_players == 2:
                        del self.adjust_num_players_menu["-"]
                        self.adjust_num_players_menu["+"] = self.player_button_menu["Player 3"]
                    else:
                        self.adjust_num_players_menu["+"] = self.player_button_menu["Player " + str(config.num_players + 1)]
                        self.adjust_num_players_menu["-"] = self.player_button_menu["Player " + str(config.num_players + 2)]
                self.active_player = self.player_buttons[0]
                return True
            
    def tile_hover(self):
        pass

    def interaction(self):
        currPlayer = self.player_buttons.index(self.active_player)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x, y, z = utils.click_to_hex(mouse_x, mouse_y)
        column, row = utils.hex_coord_to_coord(x, y, z)
        tile = self.generated_map.get_tile(row, column)
        if tile != None:
            if self.active_button == "Remove":
                if tile.unit_id is not None:
                    self.player_handler.get_player(self.unit_handler.get_unit(tile.unit_id).owner_id).remove_unit(tile.unit_id)
                    self.unit_handler.remove_unit(tile.unit_id)
            elif tile.terrain != "Mountain":
                if tile.unit_id is not None and (currPlayer != self.unit_handler.get_unit(tile.unit_id).owner_id or self.unit_handler.get_unit(tile.unit_id).type != self.active_button):
                    self.player_handler.get_player(self.unit_handler.get_unit(tile.unit_id).owner_id).remove_unit(tile.unit_id)
                    self.unit_handler.remove_unit(tile.unit_id)
                    self.player_handler.get_player(currPlayer).place_unit(self.active_button, x, y, z)
                elif tile.unit_id is None:
                    self.player_handler.get_player(currPlayer).place_unit(self.active_button, x, y, z)
        return
    

class UnitControlMenu:
    def __init__(self, screen, parent_menu, generated_map, player_handler, unit_handler):
        self.screen = screen
        self.parent_menu = parent_menu
        self.generated_map = generated_map
        self.player_handler = player_handler
        self.unit_handler = unit_handler
        
        self.initX = 0
        self.initY = 0
        self.clicked = False
        self.dragging = False
        self.clicked_button = False
        self.interaction_done = False
        
        self.active_tile = None
        self.active_unit = None
        
        self.current_player = 0
        
        self.button_width = 100
        self.button_height = 40
        self.padding = 10
        self.valid_hover = True
        buttons = ["Move", "Attack", "Fortify", "Heal", "Skip Turn", "Cancel", "De-select"]
        
        self.active_button = None

        self.button_menu = {}

        for i, name in enumerate(reversed(buttons)):
            x = WIDTH - self.button_width - self.padding
            y = HEIGHT - self.padding - (i + 1) * self.button_height - i * self.padding
            self.button_menu[name] = pygame.Rect(x, y, self.button_width, self.button_height)
            

    def left_click(self, event):
        print("Unit Control Menu Left Click")
        self.clicked = True
        if self.is_clicked():
            self.clicked_button = True
        self.set_init(event)
    
    def left_click_up(self, current_player):
        self.current_player = current_player
        print("Unit Control Menu Left Click Up")
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tile = self.generated_map.get_tile_hex(*utils.click_to_hex(mouse_x, mouse_y))
        unit = self.unit_handler.get_unit(tile.unit_id) if tile != None else None
        print("Active Unit:", self.active_unit)
        if self.clicked_button:
            self.button_clicked() 
        elif self.clicked and self.dragging == False and tile != None and unit != None and unit.owner_id == current_player and self.active_button == None:
            self.reset()
            self.active_tile = tile
            self.active_unit = unit
            self.generated_map.selected_tile = self.active_tile
            self.parent_menu.display_unit_ui = True
            if unit.destination != None:
                unit.move_to_hover(unit.destination)
        elif self.clicked and self.dragging == False and self.active_button != None:
            self.interaction()
        elif self.clicked and self.dragging == False:
            self.reset()
        

        self.dragging = False
        self.clicked = False
        self.clicked_button = False
        self.interaction_done = False
        self.valid_hover = True
    
    def right_click(self, event):
        return
    
    def right_click_up(self, event):
        return
    
    def mouse_move(self, event):
        if self.clicked and not self.clicked_button:
            self.valid_hover = False
            self.move_map(event)
        if not self.clicked and self.active_button != None:
            self.tile_hover()
         
    def zoom(self, event):
        if event.y > 0 and config.hex["radius"] < config.hex["max_radius"]:
            config.hex["radius"] += 5
            config.hex["inner_radius"] = config.hex["radius"] * 0.866025404
            config.map_settings["offsetX"] -= ZOOM_SCALE * COLUMNS
            config.map_settings["offsetY"] += ZOOM_SCALE * ROWS
        elif event.y < 0 and config.hex["radius"] > config.hex["min_radius"]:
            config.hex["radius"] -= 5
            config.hex["inner_radius"] = config.hex["radius"] * 0.866025404
            config.map_settings["offsetX"] += ZOOM_SCALE * COLUMNS
            config.map_settings["offsetY"] -= ZOOM_SCALE * ROWS

    def move_map(self, event):
        if self.active_button != None and self.active_button != "Move":
            self.interaction()
        else:
            self.dragging = True
            config.map_settings["offsetX"] += event.pos[0] - self.initX
            config.map_settings["offsetY"] += event.pos[1] - self.initY
            self.initX = event.pos[0]
            self.initY = event.pos[1]
            
    def reset(self):
        print("Resetting Unit Control Menu")
        if self.active_unit != None:
            print("fuck")
            self.active_unit.clear_hover_path()
        else:
            print("bryuh")
        self.active_unit = None
        self.active_tile = None
        self.active_button = None
        self.clicked = False
        self.dragging = False
        self.clicked_button = False
        self.generated_map.selected_tile = None
        self.unit_handler.unit_selected = False
        self.unit_handler.selected_unit = None
        self.parent_menu.display_unit_ui = False

    def set_init(self, event):
        self.initX = event.pos[0]
        self.initY = event.pos[1]
    
    def create_menu(self):
        for key in self.button_menu.keys():
            self.draw_button(key, self.button_menu[key], self.active_button == key)
        self.draw_unit_info()
            
    def draw_button(self, text, rect, is_hovered):
        font = pygame.font.SysFont(None, 24)
        pygame.draw.rect(self.screen, DARK_GRAY if self.is_hovered(rect) or is_hovered else GRAY, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)  # Border
        text_surf = font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
        
    def draw_unit_info(self):
        if self.active_unit is not None:
            box_width = 200
            box_height = 120
            box_x = 10
            box_y = self.screen.get_height() - box_height - 10

            pygame.draw.rect(self.screen, (220, 220, 220), (box_x, box_y, box_width, box_height))
            pygame.draw.rect(self.screen, (0, 0, 0), (box_x, box_y, box_width, box_height), 2)

            font = pygame.font.SysFont(None, 24)

            lines = [
                f"Health: {self.active_unit.health}",
                f"Offensive Strength: {self.active_unit.attack}",
                f"Defensive Strength: {self.active_unit.defense}",
                f"Movement: {self.active_unit.remaining_movement}/{self.active_unit.movement}"
            ]

            for i, line in enumerate(lines):
                text_surf = font.render(line, True, (0, 0, 0))
                self.screen.blit(text_surf, (box_x + 10, box_y + 10 + i * 25))
    
    def is_hovered(self, rect):
        if not self.valid_hover:
            return False
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_x, mouse_y):
            return True
        return False
    
    def is_clicked(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for key in self.button_menu.keys():
            if self.button_menu[key].collidepoint(mouse_x, mouse_y):
                return True
        
        return False

    def button_clicked(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        print("Button Clicked")
        for key in self.button_menu.keys():
            if self.button_menu[key].collidepoint(mouse_x, mouse_y):
                if key == "De-select":
                    print(self.active_unit)
                    self.reset()

                elif self.active_button == key:
                    self.active_button = None
                else:
                    self.active_button = key
        print("Active Button:", self.active_button)
        if self.active_unit != None and self.active_unit.destination != None:
            print("lol")
            self.active_unit.move_to_hover(self.active_unit.destination)
                    
    def tile_hover(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x, y, z = utils.click_to_hex(mouse_x, mouse_y)
        column, row = utils.hex_coord_to_coord(x, y, z)
        tile = self.generated_map.get_tile(row, column)
        if self.active_tile != None:
            if self.active_button == "Move":
                self.unit_handler.get_unit(self.active_tile.unit_id).move_to_hover((x, y, z))
        pass


    def interaction(self):
        print("Unit Control Menu Interaction")
        self.interaction_done = True
        unit = self.unit_handler.get_unit(self.active_tile.unit_id)
        currPlayer = 0
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x, y, z = utils.click_to_hex(mouse_x, mouse_y)
        column, row = utils.hex_coord_to_coord(x, y, z)
        tile = self.generated_map.get_tile(row, column)
        if self.active_tile != None:
            if self.active_button == "Move" and not self.dragging:
                unit.clear_hover_path()
                movement_remaining = unit.move_to((x, y, z))
                self.active_button = None
                if movement_remaining == 0:
                    self.reset()

                else:
                    self.active_tile = self.generated_map.get_tile_hex(*unit.coord)
                    self.generated_map.selected_tile = self.active_tile
                self.player_handler.get_player(self.current_player).update_visibility()

                
                
        return
    
class GameControlsInterface:
    def __init__(self, screen, game_manager):
        self.screen = screen
        self.game_manager = game_manager
        
        self.initX = 0
        self.initY = 0
        self.clicked = False
        self.dragging = False
        self.clicked_button = False
        
        self.button_width = 100
        self.button_height = 40
        self.padding = 10
        self.valid_hover = True
        self.active_button = "Start"
        
        buttons = ["Start", "End"]
        self.button_menu = {}
        

        
        x = self.padding
        y = self.padding + 0 * (self.button_height + self.padding)
        self.button_menu["Start"] = pygame.Rect(x, y, self.button_width, self.button_height)
        self.button_menu["End"] = pygame.Rect(x, y, self.button_width, self.button_height)

    def left_click(self, event):
        self.clicked = True
        if self.is_clicked():
            self.clicked_button = True
        self.set_init(event)
    
    def left_click_up(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if self.clicked_button:
            self.button_clicked()   

        self.dragging = False
        self.clicked = False
        self.clicked_button = False
        self.valid_hover = True
        return self.active_button
        
    
    def right_click(self, event):
        return
    
    def right_click_up(self, event):
        return
    
    def mouse_move(self, event):
        if self.clicked and not self.clicked_button:
            self.valid_hover = False
        if not self.clicked and self.active_button != None:
            self.tile_hover()
         

    def set_init(self, event):
        self.initX = event.pos[0]
        self.initY = event.pos[1]
    
    def create_menu(self):
        
        self.draw_button(self.active_button, self.button_menu[self.active_button], False)

    def draw_button(self, text, rect, is_hovered):
        font = pygame.font.SysFont(None, 24)
        pygame.draw.rect(self.screen, DARK_GRAY if self.is_hovered(rect) or is_hovered else GRAY, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)  # Border
        text_surf = font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
    
    def is_hovered(self, rect):
        if not self.valid_hover:
            return False
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_x, mouse_y):
            return True
        return False
    
    def is_clicked(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.button_menu[self.active_button].collidepoint(mouse_x, mouse_y):
            return True
        return False
    
    def tile_hover(self):
        pass

    def button_clicked(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.button_menu[self.active_button].collidepoint(mouse_x, mouse_y):
            if self.active_button == "Start":
                self.active_button = "End"
                self.game_manager.start_game("Test")
            else:
                self.active_button = "Start"
                self.game_manager.end_game()


    
    
