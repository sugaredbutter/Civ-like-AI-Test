import pygame
import interactions.config as config
import interactions.utils as utils

WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
DARK_GRAY = (120, 120, 120)
BLACK = (0, 0, 0)
WIDTH = config.map_settings["pixel_width"]
HEIGHT = config.map_settings["pixel_height"]
class UserInterface:
    def __init__(self, screen, generated_map, player_handler, unit_handler):
        self.screen = screen
        self.generated_map = generated_map
        self.player_handler = player_handler
        self.unit_handler = unit_handler
        
        self.button_width = 100
        self.button_height = 40
        self.padding = 10
        self.valid_hover = True
        self.active_button = None
        self.active_menu = self
                
        self.Menus = [PainterMenu(screen, self, self, self.generated_map), TerrainMenu(screen, self, self, self.generated_map), UnitMenu(screen, self, self, self.generated_map, self.player_handler, self.unit_handler)]
        menus_list = ["Biome Paint", "Terrain Paint", "Unit Placer"]
        self.button_menu = {}

        for i, name in enumerate(menus_list):
            x = WIDTH - self.button_width - self.padding
            y = self.padding + i * (self.button_height + self.padding)
            self.button_menu[name] = (pygame.Rect(x, y, self.button_width, self.button_height), self.Menus[i])
    
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
    def __init__(self, screen, main_menu, parent_menu, generated_map):
        self.screen = screen
        self.main_menu = main_menu
        self.parent_menu = parent_menu
        self.generated_map = generated_map
        
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

    def interaction(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x, y, z = utils.click_to_hex(mouse_x, mouse_y)
        row, column = utils.hex_coord_to_coord(x, y, z)
        tile = self.generated_map.get_tile(row, column)
        if tile != None:
            tile.biome = self.active_button
        return
    
class TerrainMenu:
    def __init__(self, screen, main_menu, parent_menu, generated_map):
        self.screen = screen
        self.main_menu = main_menu
        self.parent_menu = parent_menu
        self.generated_map = generated_map
        
        self.button_width = 100
        self.button_height = 40
        self.padding = 10
        self.valid_hover = True
        self.active_button = None
        buttons = ["Back", "Flat", "Hill"]
        self.button_menu = {}

        for i, name in enumerate(buttons):
            x = WIDTH - self.button_width - self.padding
            y = self.padding + i * (self.button_height + self.padding)
            self.button_menu[name] = pygame.Rect(x, y, self.button_width, self.button_height)
    
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

    def interaction(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x, y, z = utils.click_to_hex(mouse_x, mouse_y)
        row, column = utils.hex_coord_to_coord(x, y, z)
        tile = self.generated_map.get_tile(row, column)
        if tile != None:
            tile.terrain = self.active_button
        return
    
class UnitMenu:
    def __init__(self, screen, main_menu, parent_menu, generated_map, player_handler, unit_handler):
        self.screen = screen
        self.main_menu = main_menu
        self.parent_menu = parent_menu
        self.generated_map = generated_map
        self.player_handler = player_handler
        self.unit_handler = unit_handler
        
        self.button_width = 100
        self.button_height = 40
        self.padding = 10
        self.valid_hover = True
        self.active_button = None
        buttons = ["Back", "Melee", "Ranged", "Remove"]
        self.button_menu = {}

        for i, name in enumerate(buttons):
            x = WIDTH - self.button_width - self.padding
            y = self.padding + i * (self.button_height + self.padding)
            self.button_menu[name] = pygame.Rect(x, y, self.button_width, self.button_height)
    
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

    def interaction(self):
        currPlayer = 0
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x, y, z = utils.click_to_hex(mouse_x, mouse_y)
        row, column = utils.hex_coord_to_coord(x, y, z)
        tile = self.generated_map.get_tile(row, column)
        if tile != None:
            if self.active_button == "Remove":
                if tile.unit_id is not None:
                    self.player_handler.get_player(self.unit_handler.get_unit(tile.unit_id).owner_id).remove_unit(tile.unit_id)
                    self.unit_handler.remove_unit(tile.unit_id)
                    tile.unit_id = None
            else:
                if tile.unit_id is not None and (currPlayer != self.unit_handler.get_unit(tile.unit_id).owner_id or self.unit_handler.get_unit(tile.unit_id).type != self.active_button):
                    self.player_handler.get_player(self.unit_handler.get_unit(tile.unit_id).owner_id).remove_unit(tile.unit_id)
                    self.unit_handler.remove_unit(tile.unit_id)
                    self.player_handler.get_player(currPlayer).place_unit(self.active_button, x, y, z)
                elif tile.unit_id is None:
                    self.player_handler.get_player(currPlayer).place_unit(self.active_button, x, y, z)
        return
    

class UnitControlMenu:
    def __init__(self, screen, main_menu, parent_menu, generated_map, unit_controls, player_handler, unit_handler):
        self.screen = screen
        self.main_menu = main_menu
        self.parent_menu = parent_menu
        self.generated_map = generated_map
        self.unit_controls = unit_controls
        self.player_handler = player_handler
        self.unit_handler = unit_handler
        
        self.active_tile = None
        
        self.button_width = 100
        self.button_height = 40
        self.padding = 10
        self.valid_hover = True
        self.active_button = None
        buttons = ["Move", "Attack", "Fortify", "Heal", "Skip Turn", "De-select"]
        self.button_menu = {}

        for i, name in enumerate(reversed(buttons)):
            x = WIDTH - self.button_width - self.padding
            y = HEIGHT - self.padding - (i + 1) * self.button_height - i * self.padding
            self.button_menu[name] = pygame.Rect(x, y, self.button_width, self.button_height)

    
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
                if key == "De-select":
                    self.main_menu.active_menu = self.parent_menu
                    self.active_button = None
                    self.unit_controls.unit_selected = False
                    self.unit_controls.selected_unit = None
                    self.generated_map.selected_tile = None
                elif self.active_button == key:
                    self.active_button = None
                else:
                    self.active_button = key

    def interaction(self):
        currPlayer = 0
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x, y, z = utils.click_to_hex(mouse_x, mouse_y)
        row, column = utils.hex_coord_to_coord(x, y, z)
        tile = self.generated_map.get_tile(row, column)
        if self.active_tile != None:
            if self.active_button == "Move":
                self.unit_handler.get_unit(self.active_tile.unit_id).move_to((x, y, z))
                
        return