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
                
        self.Menus = [PainterMenu(screen, self, self, generated_map, self.tile_controls), TerrainMenu(screen, self, self, generated_map, self.tile_controls), UnitMenu(screen, self, self, self.generated_map, self.player_handler, self.unit_handler, self.tile_controls)]
        menus_list = ["Biome Paint", "Terrain Paint", "Unit Placer"]
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
        elif self.clicked and self.dragging == False and self.generated_map.get_tile_hex(*utils.click_to_hex(mouse_x, mouse_y)) != None and self.active_button == None:
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
        row, column = utils.hex_coord_to_coord(x, y, z)
        tile = self.generated_map.get_tile(row, column)
        if tile != None:
            tile.biome = self.active_button
        return
    
class TerrainMenu:
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
        buttons = ["Back", "Flat", "Hill"]
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
        row, column = utils.hex_coord_to_coord(x, y, z)
        tile = self.generated_map.get_tile(row, column)
        if tile != None:
            tile.set_terrain(self.active_button)
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
        row, column = utils.hex_coord_to_coord(x, y, z)
        tile = self.generated_map.get_tile(row, column)
        if tile != None:
            if self.active_button == "Remove":
                if tile.unit_id is not None:
                    self.player_handler.get_player(self.unit_handler.get_unit(tile.unit_id).owner_id).remove_unit(tile.unit_id)
                    self.unit_handler.remove_unit(tile.unit_id)
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
        
        self.initX = 0
        self.initY = 0
        self.clicked = False
        self.dragging = False
        self.clicked_button = False
        
        self.active_tile = None
        
        self.button_width = 100
        self.button_height = 40
        self.padding = 10
        self.valid_hover = True
        buttons = ["Move", "Attack", "Fortify", "Heal", "Skip Turn", "De-select"]
        
        self.active_button = None

        self.button_menu = {}

        for i, name in enumerate(reversed(buttons)):
            x = WIDTH - self.button_width - self.padding
            y = HEIGHT - self.padding - (i + 1) * self.button_height - i * self.padding
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

                    
    def tile_hover(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x, y, z = utils.click_to_hex(mouse_x, mouse_y)
        row, column = utils.hex_coord_to_coord(x, y, z)
        tile = self.generated_map.get_tile(row, column)
        if self.active_tile != None:
            if self.active_button == "Move":
                self.unit_handler.get_unit(self.active_tile.unit_id).move_to_hover((x, y, z))
        pass


    def interaction(self):
        unit = self.unit_handler.get_unit(self.active_tile.unit_id)
        currPlayer = 0
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x, y, z = utils.click_to_hex(mouse_x, mouse_y)
        row, column = utils.hex_coord_to_coord(x, y, z)
        tile = self.generated_map.get_tile(row, column)
        if self.active_tile != None:
            if self.active_button == "Move":
                unit.clear_hover_path()
                unit.move_to((x, y, z))
                
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


    
    
