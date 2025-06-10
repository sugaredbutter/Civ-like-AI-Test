import pygame
import interactions.config as config
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
        self.game_manager = None
        
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
                
        self.current_player = 0
                
        self.Menus = [None]
        menus_list = ["Next Turn"]
        self.button_menu = {}
        
        ui_list = ["Player"]
        self.ui_menu = {}

        for i, name in enumerate(menus_list):
            x = WIDTH - self.button_width - self.padding
            y = self.padding + i * (self.button_height + self.padding)
            self.button_menu[name] = (pygame.Rect(x, y, self.button_width, self.button_height), self.Menus[i])
            
        for i, name in enumerate(ui_list):
            x = self.padding + (i + 1) * (self.button_width + self.padding)
            y = self.padding
            self.ui_menu[name] = (pygame.Rect(x, y, self.button_width, self.button_height), "Player 1")
            
    def end_game_reset(self):
        self.initX = 0
        self.initY = 0
        self.clicked = False
        self.dragging = False
        self.clicked_button = False
        self.valid_hover = True
        self.active_button = None
        self.active_menu = self
        self.tile_controls = controls.TileClickControls(self.screen, self, self.generated_map, self.player_handler, self.unit_handler)

            
    def left_click(self, event):
        self.clicked = True
        if self.is_clicked():
            self.clicked_button = True
        self.set_init(event)
    
    def left_click_up(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tile = self.generated_map.get_tile_hex(*utils.click_to_hex(mouse_x, mouse_y))
        unit = self.unit_handler.get_unit(tile.unit_id) if tile != None else None
        if self.clicked_button and self.is_clicked():
            self.button_clicked()   
        elif self.clicked and self.dragging == False and tile != None and unit != None and unit.owner_id == self.current_player and self.active_button == None:
            self.tile_controls.click()
        elif self.clicked and self.dragging == False:
            self.tile_controls.reset()  

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
        for key in self.ui_menu.keys():
            self.draw_UI(self.ui_menu[key][1], self.ui_menu[key][0])
    
    def draw_button(self, text, rect, is_hovered):
        font = pygame.font.SysFont(None, 24)
        pygame.draw.rect(self.screen, DARK_GRAY if self.is_hovered(rect) or is_hovered else GRAY, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)  # Border
        text_surf = font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
        
    def draw_UI(self, text, rect):
        font = pygame.font.SysFont(None, 24)
        pygame.draw.rect(self.screen, GRAY, rect)
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
                    self.game_manager.next_turn()
                    
    def update_UI(self, player):
        self.current_player = player
        self.ui_menu["Player"] = (self.ui_menu["Player"][0], f"Player {player + 1}")
        
