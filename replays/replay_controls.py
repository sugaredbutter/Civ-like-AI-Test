import pygame
import config as config
import utils as utils
import interactions.interfaces.user_interface as ui

WIDTH = config.map_settings["pixel_width"]
HEIGHT = config.map_settings["pixel_height"]
ROWS, COLUMNS = config.map_settings["tile_height"], config.map_settings["tile_width"]
ZOOM_SCALE = config.map_settings["zoom"]

class MouseControls:
    def __init__(self, screen, game_state):
        self.screen = screen
        self.game_state = game_state
        self.initX = 0
        self.initY = 0
        self.clicked = False
        self.dragging = False
        

    def set_init(self, event):
        self.initX = event.pos[0]
        self.initY = event.pos[1]
         

    def left_click(self, event):
        self.clicked = True

        self.set_init(event)
        
    def left_click_up(self, event):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tile = self.game_state.map.get_tile_hex(*utils.click_to_hex(mouse_x, mouse_y))
        unit = self.game_state.units.get_unit(tile.unit_id) if tile != None else None
        

        self.dragging = False
        self.clicked = False

    def right_click(self, event):
        return

    def right_click_up(self, event):
        return

    def key_down(self, event):
        return

    def mouse_move(self, event):
        if self.clicked:
            self.valid_hover = False
            self.move_map(event)
                
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