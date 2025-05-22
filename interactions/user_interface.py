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
    def __init__(self, screen, generated_map):
        self.screen = screen
        self.generated_map = generated_map
        
        
        self.button_width = 100
        self.button_height = 40
        self.padding = 10
        self.valid_hover = True
        self.active_button = None
        self.active_menu = self
                
        self.Menus = [PainterMenu(screen, self, self, self.generated_map), TerrainMenu(screen, self, self, self.generated_map)]
        menus_list = ["Biome Paint", "Terrain Paint"]
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