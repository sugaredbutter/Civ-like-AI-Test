import pygame
import config as config
import utils as utils


WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
DARK_GRAY = (120, 120, 120)
BLACK = (0, 0, 0)
WIDTH = config.map_settings["pixel_width"]
HEIGHT = config.map_settings["pixel_height"]
ROWS, COLUMNS = config.map_settings["tile_height"], config.map_settings["tile_width"]
ZOOM_SCALE = config.map_settings["zoom"]

class GameControlsInterface:
    def __init__(self, screen, game_manager):
        self.screen = screen
        self.game_manager = game_manager
        self.start_manager = StartGameInterface(self, screen, game_manager)
        
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
        self.active_menu = self

        
        buttons = ["Start", "End"]
        self.button_menu = {}
        

        
        x = self.padding
        y = self.padding + 0 * (self.button_height + self.padding)
        self.button_menu["Start"] = pygame.Rect(x, y, self.button_width, self.button_height)
        self.button_menu["End"] = pygame.Rect(x, y, self.button_width, self.button_height)

    def left_click(self, event):
        print("lol")
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
                self.game_manager.setup()
                self.active_menu = self.start_manager
            else:
                self.active_button = "Start"
                self.game_manager.end_game()


class StartGameInterface:
    def __init__(self, game_controls, screen, game_manager):
        self.game_controls = game_controls
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
        self.active_button = None
        
        buttons = ["Test", "Player vs AI", "AI vs AI", "Back"]
        self.button_menu = {}
        

        
        for i, name in enumerate(buttons):
            x = WIDTH / 2 - self.padding / 2 - self.button_width - self.padding - self.button_width + i * (self.button_width + self.padding)
            y = HEIGHT / 2 - self.button_width / 2
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
                    self.game_controls.active_menu = self.game_controls
                elif key == "Test":
                    self.game_manager.start_game("Test")
                    self.game_controls.active_menu = self.game_controls

