import pygame
import config as config
import utils as utils
import interactions.controls as controls
import math
from map_generator.map_generator_config import MapConfig
from players.units_utils import UnitUtils
from players.units_utils import UnitMove
from players.units_utils import UnitVisibility
from players.units_utils import UnitAttack

WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
DARK_GRAY = (120, 120, 120)
BLACK = (0, 0, 0)
WIDTH = config.map_settings["pixel_width"]
HEIGHT = config.map_settings["pixel_height"]
ROWS, COLUMNS = config.map_settings["tile_height"], config.map_settings["tile_width"]
ZOOM_SCALE = config.map_settings["zoom"]

class UserInterface:
    def __init__(self, screen, game_state):
        self.screen = screen
        self.game_state = game_state
        
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
                        
        self.Menus = [PainterMenu(screen, self, self, game_state), TerrainMenu(screen, self, self, game_state), FeatureMenu(screen, self, self, game_state), UnitMenu(screen, self, self, game_state), MapGenerationMenu(screen, self, self, game_state)]
        menus_list = ["Biomes", "Terrain", "Features", "Units", "Map Gen"]
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
        config.map_change = True

    def move_map(self, event):
        if self.active_button != None:
            self.interaction()
        else:
            self.dragging = True
            config.map_settings["offsetX"] += event.pos[0] - self.initX
            config.map_settings["offsetY"] += event.pos[1] - self.initY
            self.initX = event.pos[0]
            self.initY = event.pos[1]
            config.map_change = True


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
    def __init__(self, screen, main_menu, parent_menu, game_state):
        self.screen = screen
        self.main_menu = main_menu
        self.parent_menu = parent_menu
        self.game_state = game_state
        
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
        config.map_change = True

    def move_map(self, event):
        if self.active_button != None:
            self.interaction()
        else:
            self.dragging = True
            config.map_settings["offsetX"] += event.pos[0] - self.initX
            config.map_settings["offsetY"] += event.pos[1] - self.initY
            self.initX = event.pos[0]
            self.initY = event.pos[1]
            config.map_change = True

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
        tile = self.game_state.map.get_tile(row, column)
        if tile != None:
            tile.set_biome(self.active_button)
        return
    
class TerrainMenu:
    def __init__(self, screen, main_menu, parent_menu, game_state):
        self.screen = screen
        self.main_menu = main_menu
        self.parent_menu = parent_menu
        self.game_state = game_state
        
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
            config.map_change = True

    def move_map(self, event):
        if self.active_button != None:
            self.interaction()
        else:
            self.dragging = True
            config.map_settings["offsetX"] += event.pos[0] - self.initX
            config.map_settings["offsetY"] += event.pos[1] - self.initY
            self.initX = event.pos[0]
            self.initY = event.pos[1]
            config.map_change = True

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
        tile = self.game_state.map.get_tile(row, column)
        if tile != None:
            tile.set_terrain(self.active_button)
            unit_id = tile.unit_id
            if unit_id != None and tile.terrain == "Mountain":
                unit = self.game_state.units.get_unit(unit_id)
                unit_owner = self.game_state.players.get_player(unit.owner_id)
                unit_owner.remove_unit(unit_id)
        return
    
class FeatureMenu:
    def __init__(self, screen, main_menu, parent_menu, game_state):
        self.screen = screen
        self.main_menu = main_menu
        self.parent_menu = parent_menu
        self.game_state = game_state
        
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
        config.map_change = True

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
            config.map_change = True

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
                    self.game_state.map.selected_edge = None
                    self.game_state.map.hovered_tile = None

                elif self.active_button == key:
                    self.active_button = None
                    self.game_state.map.selected_edge = None
                    self.game_state.map.hovered_tile = None

                else:
                    self.active_button = key
                    self.game_state.map.selected_edge = None
                    self.game_state.map.hovered_tile = None


    def tile_hover(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x, y, z = utils.click_to_hex(mouse_x, mouse_y)
        column, row = utils.hex_coord_to_coord(x, y, z)
        tile = self.game_state.map.get_tile(row, column)
        if tile != None:
            if self.active_button == "River":
                active_edge = utils.pos_to_edge(x, y, z)
                if active_edge is not None:
                    self.game_state.map.selected_edge = active_edge
                    self.game_state.map.hovered_tile = tile
                else:
                    self.game_state.map.selected_edge = None
                    self.game_state.map.hovered_tile = None
                


    def interaction(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x, y, z = utils.click_to_hex(mouse_x, mouse_y)
        column, row = utils.hex_coord_to_coord(x, y, z)
        tile = self.game_state.map.get_tile(row, column)
        if tile != None:
            if self.active_button == "River":
                edge = utils.pos_to_edge(x, y, z)
                if edge != None:
                    if self.dragging == False:
                        self.adding = not tile.rivers[edge]
                    self.game_state.map.selected_edge = edge
                    self.game_state.map.hovered_tile = tile

                    self.game_state.map.place_river(x, y, z, edge, self.adding)
                    self.active_tile = tile
                    self.active_edge = edge
            else:
                if self.dragging == False:
                    self.adding = False if tile.feature == "Forest" else True
                tile.set_feature(self.active_button, self.adding)
            
        return
    
class UnitMenu:
    def __init__(self, screen, main_menu, parent_menu, game_state):
        self.screen = screen
        self.main_menu = main_menu
        self.parent_menu = parent_menu
        self.game_state = game_state
        
        self.initX = 0
        self.initY = 0
        self.clicked = False
        self.dragging = False
        self.clicked_button = False
        
        self.button_width = 100
        self.button_height = 40
        self.padding = 10
        self.valid_hover = True

        buttons = ["Back", "Melee", "Ranged", "Cavalry", "Remove"]
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
            if self.active_button:
                self.interaction()
            else:
                self.valid_hover = False
                self.move_map(event)

        if not self.clicked and self.active_button is not None:
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
        config.map_change = True

    def move_map(self, event):

        self.dragging = True
        config.map_settings["offsetX"] += event.pos[0] - self.initX
        config.map_settings["offsetY"] += event.pos[1] - self.initY
        self.initX = event.pos[0]
        self.initY = event.pos[1]
        config.map_change = True

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
                    self.game_state.players.add_player()

                    if config.num_players == 4:
                        del self.adjust_num_players_menu["+"]
                        self.adjust_num_players_menu["-"] = self.player_button_menu["Player 5"]
                    else:
                        self.adjust_num_players_menu["+"] = self.player_button_menu["Player " + str(config.num_players + 1)]
                        self.adjust_num_players_menu["-"] = self.player_button_menu["Player " + str(config.num_players + 2)]

                elif key == "-" and config.num_players > 2:
                    config.num_players -= 1
                    self.game_state.players.remove_player()
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
        tile = self.game_state.map.get_tile(row, column)
        if tile != None:
            if self.active_button == "Remove":
                if tile.unit_id is not None:
                    self.game_state.players.get_player(self.game_state.units.get_unit(tile.unit_id).owner_id).remove_unit(tile.unit_id)
                    self.game_state.units.remove_unit(tile.unit_id)
            elif tile.terrain != "Mountain":
                if tile.unit_id is not None and (currPlayer != self.game_state.units.get_unit(tile.unit_id).owner_id or self.game_state.units.get_unit(tile.unit_id).type != self.active_button):
                    self.game_state.players.get_player(self.game_state.units.get_unit(tile.unit_id).owner_id).remove_unit(tile.unit_id)
                    self.game_state.units.remove_unit(tile.unit_id)
                    self.game_state.players.get_player(currPlayer).place_unit(self.active_button, x, y, z)
                elif tile.unit_id is None:
                    self.game_state.players.get_player(currPlayer).place_unit(self.active_button, x, y, z)
        return
    

class MapGenerationMenu:
    def __init__(self, screen, main_menu, parent_menu, game_state):
        self.screen = screen
        self.main_menu = main_menu
        self.parent_menu = parent_menu
        self.game_state = game_state
        
        self.initX = 0
        self.initY = 0
        self.clicked = False
        self.dragging = False
        self.clicked_button = False
        self.clicked_slider = False
        self.active_slider = None
        self.slider_curr_value = -1

        self.button_width = 100
        self.button_height = 40
        self.padding = 10

        self.slider_text_height = 25
        self.slider_length = self.button_width
        self.slider_height = 5
        self.knob_radius = 10
        self.min_val = 0
        self.max_val = 5

        self.valid_hover = True
        self.active_button = None
        interactables = ["Back", "Variability", "Temperature", "Moisture", "Generate"]
        interactables_config = [None, MapConfig.variability, MapConfig.temperature, MapConfig.moisture, None]
        buttons = ["Back", "Generate"]
        sliders = ["Variability", "Temperature", "Moisture"]
        self.button_menu = {}
        self.slider_menu = {}

        current_y = self.padding
        for i, name in enumerate(interactables):
            if name in buttons:
                x = WIDTH - self.button_width - self.padding
                y = current_y
                current_y += self.button_height + self.padding
                self.button_menu[name] = pygame.Rect(x, y, self.button_width, self.button_height)
            else:
                x = WIDTH - self.slider_length - self.padding
                y = current_y
                current_y += self.slider_text_height + self.slider_height + 2 * self.padding
                self.slider_menu[name] = [x, y, interactables_config[i]]
    
    def left_click(self, event):
        self.clicked = True
        if self.is_clicked():
            self.clicked_button = True
        elif self.is_clicked_slider():
            self.clicked_slider = True
        self.set_init(event)
    
    def left_click_up(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if self.clicked_button:
            self.button_clicked()
        elif self.clicked_slider:
            self.slider_clicked()   
        elif self.active_button != None:
            self.interaction()

        self.dragging = False
        self.clicked = False
        self.clicked_button = False
        self.clicked_slider = False
        self.active_slider = None
        self.slider_curr_value = -1
        self.valid_hover = True
    
    def right_click(self, event):
        return
    
    def right_click_up(self, event):
        return
    
    def mouse_move(self, event):
        if self.clicked and not self.clicked_button and not self.clicked_slider:
            if self.active_button:
                self.interaction()
            else:
                self.valid_hover = False
                self.move_map(event)
        if not self.clicked and self.active_button is not None:
            self.tile_hover()
        if self.clicked_slider:
            self.update_slider()
        
         
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
        config.map_change = True

    def move_map(self, event):
        self.dragging = True
        config.map_settings["offsetX"] += event.pos[0] - self.initX
        config.map_settings["offsetY"] += event.pos[1] - self.initY
        self.initX = event.pos[0]
        self.initY = event.pos[1]
        config.map_change = True

    def set_init(self, event):
        self.initX = event.pos[0]
        self.initY = event.pos[1]
    
    def create_menu(self):
        for key in self.button_menu.keys():
            self.draw_button(key, self.button_menu[key], self.active_button == key)
        for key in self.slider_menu.keys():
            slider = self.slider_menu[key]
            self.draw_slider(slider[0], slider[1], slider[2], key, self.active_slider == key)

    def draw_button(self, text, rect, is_hovered):
        font = pygame.font.SysFont(None, 24)
        pygame.draw.rect(self.screen, DARK_GRAY if self.is_hovered(rect) or is_hovered else GRAY, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)  # Border
        text_surf = font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw_slider(self, x, y, value, text, is_hovered):
        font = pygame.font.SysFont(None, 24)
        text_surf = font.render(text, True, BLACK)
        self.screen.blit(text_surf, (x, y))

        slider_y = y + self.slider_text_height + self.padding

        pygame.draw.line(
            self.screen,
            (200, 200, 200),
            (x, slider_y),                           # start point
            (x + self.slider_length, y + self.slider_text_height + self.padding),      # end point
            4
        )
        if text == self.active_slider:
            slider_x = x + self.slider_length / self.max_val * self.slider_curr_value
            text_surf = font.render(str(self.slider_curr_value), True, BLACK)
            self.screen.blit(text_surf, (x - self.padding * 2, slider_y - text_surf.get_size()[1]/2))
        else:
            slider_x = x + self.slider_length / self.max_val * value
            text_surf = font.render(str(value), True, BLACK)
            self.screen.blit(text_surf, (x - self.padding * 2, slider_y - text_surf.get_size()[1]/2))
        pygame.draw.circle(self.screen, DARK_GRAY if self.is_hovered_slider(slider_x, slider_y) or is_hovered else GRAY, (slider_x, slider_y), self.knob_radius)
        pygame.draw.circle(self.screen, BLACK, (slider_x, slider_y), self.knob_radius, 2)




    
    def is_hovered(self, shape):
        if not self.valid_hover:
            return False
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if shape.collidepoint(mouse_x, mouse_y):
            return True
        return False
    
    def is_hovered_slider(self, x, y):
        if not self.valid_hover:
            return False
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - x
        dy = mouse_y - y
        distance_squared = dx * dx + dy * dy
        return distance_squared <= self.knob_radius ** 2
    
    def is_clicked(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for key in self.button_menu.keys():
            if self.button_menu[key].collidepoint(mouse_x, mouse_y):
                return True
        return False
    
    def is_clicked_slider(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for key in self.slider_menu.keys():
            x = self.slider_menu[key][0]
            y = self.slider_menu[key][1]
            value = self.slider_menu[key][2]
            slider_x = x + self.slider_length / self.max_val * value
            slider_y = y + self.slider_text_height + self.padding

            dx = mouse_x - slider_x
            dy = mouse_y - slider_y
            distance_squared = dx * dx + dy * dy
            if distance_squared <= self.knob_radius ** 2:
                self.active_slider = key
                self.slider_curr_value = value
                return True
    def update_slider(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x = self.slider_menu[self.active_slider][0]
        multiple = self.slider_length / self.max_val
        closest_value = round((multiple * round((mouse_x - x) / multiple)) / multiple)
        self.slider_curr_value = max(self.min_val, min(closest_value, self.max_val))



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

    def slider_clicked(self):
        print(self.slider_menu[self.active_slider][2])
        self.slider_menu[self.active_slider][2] = self.slider_curr_value

    def interaction(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x, y, z = utils.click_to_hex(mouse_x, mouse_y)
        column, row = utils.hex_coord_to_coord(x, y, z)
        tile = self.game_state.map.get_tile(row, column)
        if tile != None:
            tile.set_biome(self.active_button)
        return

class UnitControlMenu:
    def __init__(self, screen, parent_menu, game_state, game_manager):
        self.screen = screen
        self.parent_menu = parent_menu
        self.game_state = game_state
        self.game_manager = game_manager
        
        self.initX = 0
        self.initY = 0
        self.clicked = False
        self.dragging = False
        self.clicked_button = False
        self.interaction_done = False
        
        self.active_tile = None
        self.active_unit = None
        self.enemy_unit = None

        self.display_combat_info = False
        self.combat_info = None

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
            
        self.disabled_buttons = set()
        self.buttons_no_movement = {"Attack", "Fortify", "Heal", "Skip Turn"}
        

    def left_click(self, event):
        self.clicked = True
        if self.is_clicked():
            self.clicked_button = True
        self.set_init(event)
    
    def left_click_up(self, current_player):
        self.current_player = current_player
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tile = self.game_state.map.get_tile_hex(*utils.click_to_hex(mouse_x, mouse_y))
        unit = self.game_state.units.get_unit(tile.unit_id) if tile != None else None
        if self.clicked_button:
            self.button_clicked() 
        elif self.clicked and self.dragging == False and tile != None and unit != None and unit.owner_id == current_player and (self.active_button == None or self.active_button == "Fortify" or self.active_button == "Heal"):
            self.reset()
            self.init_unit(tile, unit)
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
        config.map_change = True

    def move_map(self, event):
        if self.active_button != None and self.active_button != "Move":
            self.interaction()
        else:
            self.dragging = True
            config.map_settings["offsetX"] += event.pos[0] - self.initX
            config.map_settings["offsetY"] += event.pos[1] - self.initY
            self.initX = event.pos[0]
            self.initY = event.pos[1]
            config.map_change = True
    
    def init_unit(self, tile, unit):
        self.active_tile = tile
        self.active_unit = unit
        self.game_state.map.selected_tile = self.active_tile
        self.parent_menu.display_unit_ui = True
        if unit.destination != None:
            unit.move_to_hover(unit.destination)
        if unit.remaining_movement == 0:
            self.disabled_buttons = self.buttons_no_movement
        if unit.fortify_and_heal:
            self.active_button = "Heal"
        elif unit.fortified:
            self.active_button = "Fortify"
        if unit.health == 100:
            self.disabled_buttons.add("Heal")
        
    
    def reset(self):
        if self.active_unit != None:
            UnitMove.clear_hover_path(self.active_unit, self.active_unit.game_state)
            UnitAttack.clear_attackable(self.active_unit, self.active_unit.game_state)
        self.active_unit = None
        self.active_tile = None
        self.active_button = None
        self.clicked = False
        self.dragging = False
        self.clicked_button = False
        self.game_state.map.selected_tile = None
        self.game_state.units.unit_selected = False
        self.game_state.units.selected_unit = None
        self.parent_menu.display_unit_ui = False
        self.disabled_buttons = set()

    def set_init(self, event):
        self.initX = event.pos[0]
        self.initY = event.pos[1]
    
    def create_menu(self):
        for key in self.button_menu.keys():
            self.draw_button(key, self.button_menu[key], self.active_button == key)
        self.draw_unit_info()
        if self.display_combat_info:
            self.draw_combat_prediction()
            
    def draw_button(self, text, rect, is_hovered):
        font = pygame.font.SysFont(None, 24)
        pygame.draw.rect(self.screen, DARK_GRAY if self.is_hovered(rect) or is_hovered or text in self.disabled_buttons else GRAY, rect)
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
                f"Health: {math.ceil(self.active_unit.health)}",
                f"Offensive Strength: {math.ceil(self.active_unit.attack)}",
                f"Defensive Strength: {math.ceil(self.active_unit.defense)}",
                f"Movement: {self.active_unit.remaining_movement}/{self.active_unit.movement}",
            ]
            if self.active_unit.fortify_and_heal:
                lines.append("Fortified and Healing")
            elif self.active_unit.skip:
                lines.append("Turn Skipped")
            elif self.active_unit.fortified:
                lines.append("Fortified")

            for i, line in enumerate(lines):
                text_surf = font.render(line, True, (0, 0, 0))
                self.screen.blit(text_surf, (box_x + 10, box_y + 10 + i * 20))
    
    def draw_combat_prediction(self):
        if self.active_unit is not None:
            damage_inflicted, damage_taken, unit, enemy_unit, unit_CS, enemy_CS, unit_bonus, enemy_bonus = self.combat_info
            box_width = 200
            box_height = 120
            box_x = 10
            box_y = self.screen.get_height() - box_height * 2 - 9

            mid_point = box_x + box_width / 2

            health_bar_width = 10
            health_bar_height = 80

            unit_1_new_health = unit.health - damage_taken
            unit_2_new_health = enemy_unit.health - damage_inflicted

            pygame.draw.rect(self.screen, (220, 220, 220), (box_x, box_y, box_width, box_height))
            pygame.draw.rect(self.screen, (0, 0, 0), (box_x, box_y, box_width, box_height), 2)

            current_health_height = health_bar_height * unit.health / 100
            bar_x = mid_point - box_width / 20 - health_bar_width
            bar_y = box_y + (box_height - health_bar_height) / 2 + (health_bar_height - current_health_height)


            # Red
            pygame.draw.rect(self.screen, (255, 0, 0), (bar_x, box_y + (box_height - health_bar_height) / 2, health_bar_width, health_bar_height))

            # Damage
            health_diff = pygame.Surface((health_bar_width, health_bar_height), pygame.SRCALPHA)
            health_diff.set_alpha(210)  # Apply overall transparency


            pygame.draw.rect(
                health_diff,
                (0, 255, 0),  
                (0, health_bar_height - current_health_height, health_bar_width, current_health_height)
            )

            self.screen.blit(health_diff, (bar_x, box_y + (box_height - health_bar_height) / 2))

            # Remaining health
            if unit_1_new_health >= 0:
                pygame.draw.rect(self.screen, (0, 255, 0), (bar_x, box_y + (box_height - health_bar_height) / 2 + health_bar_height - health_bar_height * unit_1_new_health/100, health_bar_width, health_bar_height * unit_1_new_health/100))

            # Border
            pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, box_y + (box_height - health_bar_height) / 2, health_bar_width, health_bar_height), 1)



            current_health_height = health_bar_height * enemy_unit.health / 100
            bar_x = mid_point + box_width / 20
            bar_y = box_y + (box_height - health_bar_height) / 2 + (health_bar_height - current_health_height)
            pygame.draw.rect(self.screen, (255, 0, 0), (bar_x, box_y + (box_height - health_bar_height) / 2, health_bar_width, health_bar_height))

            # Damage
            health_diff = pygame.Surface((health_bar_width, health_bar_height), pygame.SRCALPHA)
            health_diff.set_alpha(210)  


            pygame.draw.rect(
                health_diff,
                (0, 255, 0),  
                (0, health_bar_height - current_health_height, health_bar_width, current_health_height)
            )

            self.screen.blit(health_diff, (bar_x, box_y + (box_height - health_bar_height) / 2))
            if unit_2_new_health >= 0:
                pygame.draw.rect(self.screen, (0, 255, 0), (bar_x, box_y + (box_height - health_bar_height) / 2 + health_bar_height - health_bar_height * unit_2_new_health/100, health_bar_width, health_bar_height * unit_2_new_health/100))
            pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, box_y + (box_height - health_bar_height) / 2, health_bar_width, health_bar_height), 1)
            
            font = pygame.font.SysFont(None, 24)
            text_x = box_x + box_width / 20
            text_y = box_y
            
            orig_hp_color = utils.get_health_color(unit.health)
            new_hp_color = utils.get_health_color(unit_1_new_health)
            unit_1_cs_color, unit_2_cs_color = utils.combat_strength_color(unit_CS, enemy_CS)
            lines = [
                ("HP:", f" {math.ceil(self.active_unit.health)}", orig_hp_color),
                ("", f"-{math.ceil(damage_taken)}", (230, 34, 34)),
                ("", f" {max(0, math.ceil(self.active_unit.health) - math.ceil(damage_taken))}", new_hp_color),
                ("CS:", f" {math.ceil(unit_CS)}", unit_1_cs_color)
            ]

            label_x = text_x
            value_x = text_x + 30  # Adjust as needed for alignment

            for i, (label, value, color) in enumerate(lines):
                label_surf = font.render(str(label), True, (0, 0, 0))
                value_surf = font.render(str(value), True, color)

                y = text_y + 10 + i * 20
                self.screen.blit(label_surf, (label_x, y))
                
                utils.blit_text_border(self.screen, str(value), (value_x, y), 1, font, (0, 0, 0))

                self.screen.blit(value_surf, (value_x, y))
                
            orig_hp_color = utils.get_health_color(enemy_unit.health)
            new_hp_color = utils.get_health_color(unit_2_new_health)
            text_x = box_x + box_width - box_width / 20
            text_y = box_y
            lines = [
                (":HP", f"{math.ceil(enemy_unit.health)} ", orig_hp_color),
                ("", f"-{math.ceil(damage_inflicted)} ", (230, 34, 34)),
                ("", f"{max(0, math.ceil(enemy_unit.health) - math.ceil(damage_inflicted))} ", new_hp_color),
                (":CS", f"{math.ceil(enemy_CS)} ", unit_2_cs_color)
            ]
            value_column_width = 40  # Width reserved for the value (adjust as needed)
            label_x = text_x
            value_x = text_x - 30  # All numbers should end here

            for i, (label, value, color) in enumerate(lines):
                label_surf = font.render(str(label), True, (0, 0, 0))
                value_surf = font.render(str(value), True, color)

                y = text_y + 10 + i * 20
                

                self.screen.blit(label_surf, (label_x - label_surf.get_width(), y))

                # Right-align value by subtracting its width from the right edge
                utils.blit_text_border(self.screen, str(value), (value_x - value_surf.get_width(), y), 1, font, (0, 0, 0))

                self.screen.blit(value_surf, (value_x - value_surf.get_width(), y))
            self.draw_combat_bonuses()
    
    def draw_combat_bonuses(self):
        damage_inflicted, damage_taken, unit, enemy_unit, unit_CS, enemy_CS, unit_bonus, enemy_bonus = self.combat_info
        box_width = 200
        box_height = 120
        box_x = 10
        box_y = self.screen.get_height() - box_height * 2 - 8 - box_height
        mid_point = box_x + box_width / 2

        
        pygame.draw.rect(self.screen, (220, 220, 220), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, (0, 0, 0), (box_x, box_y, box_width, box_height), 2)
        
        font = pygame.font.SysFont(None, 20)
        text_x = box_x + box_width / 20
        text_y = box_y
        

        label_x = text_x
        value_x = text_x + 50  # Adjust as needed for alignment
        i = 0
        for key in unit_bonus.keys():
            if unit_bonus[key] != 0:
                label_surf = font.render(key, True, (0, 0, 0))
                value_surf = font.render(str(unit_bonus[key]), True, (0, 219, 58) if unit_bonus[key] > 0 else (240, 54, 2))

                y = text_y + 10 + i * 20
                self.screen.blit(label_surf, (label_x, y))
                
                self.screen.blit(value_surf, (mid_point - 5 - value_surf.get_width(), y))
                i += 1
                
                

        text_x = box_x + mid_point + box_width / 20
        text_y = box_y
        label_x = text_x
        value_x = text_x + 50  # Adjust as needed for alignment
        i = 0
        for key in enemy_bonus.keys():
            if enemy_bonus[key] != 0:
                label_surf = font.render(key, True, (0, 0, 0))
                value_surf = font.render(str(enemy_bonus[key]), True, (0, 219, 58) if enemy_bonus[key] > 0 else (240, 54, 2))

                y = text_y + 10 + i * 20
                self.screen.blit(label_surf, (label_x, y))
                
                self.screen.blit(value_surf, (box_x + box_width - 5 - value_surf.get_width(), y))
                i += 1
    def is_hovered(self, rect):
        if not self.valid_hover:
            return False
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_x, mouse_y):
            return True
        return False
    
    def is_clicked(self):
        if self.active_unit == None:
            return False
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for key in self.button_menu.keys():
            if self.button_menu[key].collidepoint(mouse_x, mouse_y):
                return True
        
        return False

    def button_clicked(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        unit = self.game_state.units.get_unit(self.active_tile.unit_id)
        
        for key in self.button_menu.keys():
            if self.button_menu[key].collidepoint(mouse_x, mouse_y) and key not in self.disabled_buttons:
                if key == "De-select":
                    self.reset()

                elif self.active_button == key:
                    if self.active_button == "Move":
                        UnitMove.clear_hover_path(unit, unit.game_state)
                    if self.active_button == "Attack":
                        UnitAttack.clear_attackable(unit, unit.game_state)
                    self.active_button = None

                else:
                    self.active_button = key
                    UnitMove.clear_hover_path(unit, unit.game_state)
                    UnitAttack.clear_attackable(unit, unit.game_state)

                    if self.active_button == "Attack":
                        unit = self.game_state.units.get_unit(self.active_tile.unit_id)
                        UnitAttack.highlight_attackable(unit, unit.game_state)
                    if self.active_button == "Fortify":
                        unit.cancel_action()
                        unit.fortify()
                        self.reset()
                    if self.active_button == "Heal":
                        unit.cancel_action()
                        unit.heal()
                        self.reset()
                    if self.active_button == "Skip Turn":
                        unit.cancel_action()
                        unit.skip_turn()
                        self.active_button = None
                        self.reset()
                    if self.active_button == "Cancel":
                        unit.cancel_action()
                        self.active_button = None


        if self.active_unit != None and self.active_unit.destination != None:
            self.active_unit.move_to_hover(self.active_unit.destination)
                    
    def tile_hover(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x, y, z = utils.click_to_hex(mouse_x, mouse_y)
        column, row = utils.hex_coord_to_coord(x, y, z)
        tile = self.game_state.map.get_tile(row, column)
        if self.active_tile != None:
            if self.active_button == "Move":
                self.game_state.units.get_unit(self.active_tile.unit_id).move_to_hover((x, y, z))
            elif self.active_button == "Attack":
                self.combat_info = self.active_unit.attack_hover((x, y, z))
                if self.combat_info == None:
                    self.display_combat_info = False
                else:
                    self.display_combat_info = True

        pass


    def interaction(self):
        self.interaction_done = True
        unit = self.game_state.units.get_unit(self.active_tile.unit_id)
        if unit == None:
            return
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x, y, z = utils.click_to_hex(mouse_x, mouse_y)
        if self.active_button == "Move" and not self.dragging:
            UnitMove.clear_hover_path(unit, unit.game_state)
            movement_remaining = unit.move_to((x, y, z))
            if movement_remaining == 0:
                self.reset()

            else:
                self.active_tile = self.game_state.map.get_tile_hex(*unit.coord)
                self.game_state.map.selected_tile = self.active_tile

        if self.active_button == "Attack" and not self.dragging:
            movement_remaining = unit.attack_enemy((x, y, z))
            if movement_remaining == 0:
                self.reset()

            else:
                self.active_tile = self.game_state.map.get_tile_hex(*unit.coord)
                self.game_state.map.selected_tile = self.active_tile
            self.display_combat_info = False
            self.game_manager.check_win()
        if (self.active_button == "Fortify" or self.active_button == "Heal") and not self.dragging:
            self.reset()
            
        if unit.remaining_movement == 0:
            self.disabled_buttons = self.buttons_no_movement
        if unit.health == 100:
            self.disabled_buttons.add("Heal")
        self.active_button = None

        return
    

    
    
