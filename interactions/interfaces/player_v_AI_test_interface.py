import pygame
import config as config
import utils as utils
import interactions.controls as controls
import interactions.interfaces.user_interface as ui
import config as config
from Agents.agent import ScoreAgent 

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
        self.game_manager = None
        self.unit_menu = None

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
        
        self.display_unit_ui = False
                
        self.current_player = 0
                
        self.menus = [None, None]
        menus_list = ["Next Turn", "Next Unit"]
        self.button_menu = {}

        self.AI_menus = [None, None]
        AI_menus_list = ["Next Turn", "Next Action"]
        self.AI_button_menu = {}
        
        ui_list = ["Player"]
        self.ui_menu = {}

        for i, name in enumerate(menus_list):
            x = WIDTH - self.button_width - self.padding
            y = self.padding + i * (self.button_height + self.padding)
            self.button_menu[name] = (pygame.Rect(x, y, self.button_width, self.button_height), self.menus[i])

        for i, name in enumerate(AI_menus_list):
            x = WIDTH - self.button_width - self.padding
            y = self.padding + i * (self.button_height + self.padding)
            self.AI_button_menu[name] = (pygame.Rect(x, y, self.button_width, self.button_height), self.AI_menus[i])
            
        for i, name in enumerate(ui_list):
            x = self.padding + (i + 1) * (self.button_width + self.padding)
            y = self.padding
            self.ui_menu[name] = (pygame.Rect(x, y, self.button_width, self.button_height), "Player 1")
            
    def set_game_manager(self, game_manager):
        self.game_manager = game_manager
        self.unit_menu = ui.UnitControlMenu(self.screen, self, self.game_state.map, self.game_state.players, self.game_state.units, self.game_manager)



    def end_game_reset(self):
        self.initX = 0
        self.initY = 0
        self.clicked = False
        self.dragging = False
        self.clicked_button = False
        self.valid_hover = True
        self.active_button = None
        self.active_menu = self
        self.unit_menu.reset()
        self.current_player = 0
        self.ui_menu["Player"] = (self.ui_menu["Player"][0], f"Player {1}")

            
    def left_click(self, event):
        self.clicked = True
        if self.is_clicked():
            self.clicked_button = True
        elif self.current_player == 0:
            self.unit_menu.left_click(event)
        self.set_init(event)
    
    def left_click_up(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tile = self.game_state.map.get_tile_hex(*utils.click_to_hex(mouse_x, mouse_y))
        unit = self.game_state.units.get_unit(tile.unit_id) if tile != None else None
        if self.clicked_button and self.is_clicked():
            self.button_clicked()   
        elif self.current_player == 0:
            self.unit_menu.left_click_up(self.current_player)
        

        self.dragging = False
        self.clicked = False
        self.clicked_button = False
        self.valid_hover = True
    
    def right_click(self, event):
        return
    
    def right_click_up(self, event):
        return
    
    def mouse_move(self, event):
        if self.display_unit_ui:
            self.unit_menu.mouse_move(event)
        elif self.clicked and not self.clicked_button:
            self.valid_hover = False
            self.move_map(event)
        elif self.unit_menu.active_button != None:
            self.unit_menu.interaction()
         
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
        player = self.game_state.players.get_player(self.current_player)
        if player.AI == False:
            for key in self.button_menu.keys():
                self.draw_button(key, self.button_menu[key][0], self.active_button == key)
        else:
            for key in self.AI_button_menu.keys():
                self.draw_button(key, self.AI_button_menu[key][0], self.active_button == key)
        for key in self.ui_menu.keys():
            self.draw_UI(self.ui_menu[key][1], self.ui_menu[key][0])
        if self.display_unit_ui:
            self.unit_menu.create_menu()
    
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
        player = self.game_state.players.get_player(self.current_player)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if player.AI == False:
            for key in self.button_menu.keys():
                if self.button_menu[key][0].collidepoint(mouse_x, mouse_y):
                    if self.button_menu[key][1] != None:
                        self.active_menu = self.button_menu[key][1]
                    elif key == "Next Turn":
                        self.game_manager.next_turn()
                        self.unit_menu.reset()
                    elif key == "Next Unit":
                        result = self.game_manager.cycle_unit()
                        if result != None:
                            self.unit_menu.init_unit(result[0], result[1])
        else:
            for key in self.AI_button_menu.keys():
                if self.AI_button_menu[key][0].collidepoint(mouse_x, mouse_y):
                    if self.AI_button_menu[key][1] != None:
                        self.active_menu = self.AI_button_menu[key][1]
                    elif key == "Next Turn":
                        self.game_manager.next_turn()
                        self.unit_menu.reset()
                    elif key == "Next Action":
                        ScoreAgent.choose_best_action(self.current_player, self.game_state, self.game_manager)
                    
    def update_UI(self, player):
        self.current_player = player
        self.ui_menu["Player"] = (self.ui_menu["Player"][0], f"Player {player + 1}")
        