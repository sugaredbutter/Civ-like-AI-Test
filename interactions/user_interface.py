import pygame
import interactions.config as config

WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
DARK_GRAY = (120, 120, 120)
BLACK = (0, 0, 0)
WIDTH = config.map_settings["pixel_width"]
HEIGHT = config.map_settings["pixel_height"]
class UserInterface:
    def __init__(self, screen):
        self.screen = screen
        self.button_width = 100
        self.button_height = 40
        self.padding = 10
        self.valid_hover = False
        self.active_button = None
        self.terrain_buttons = {
            "Desert": pygame.Rect(WIDTH - self.button_width - self.padding, self.padding, self.button_width, self.button_height),
            "Plain": pygame.Rect(WIDTH - self.button_width - self.padding, 2*self.padding + self.button_height, self.button_width, self.button_height)
        }
    def painter(self, is_hovered):
        for key in self.terrain_buttons.keys():
            self.draw_button(key, self.terrain_buttons[key], self.active_button == key)


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
    
    def is_clicked(self, event):
        mouse_x, mouse_y = event.pos
        for key in self.terrain_buttons.keys():
            if self.terrain_buttons[key].collidepoint(mouse_x, mouse_y):
                return True
        return False

    def button_clicked(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for key in self.terrain_buttons.keys():
            if self.terrain_buttons[key].collidepoint(mouse_x, mouse_y):
                if self.active_button == key:
                    self.active_button = None
                else:
                    self.active_button = key
                
        
        
        
    
    