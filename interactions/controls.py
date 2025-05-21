import pygame
import interactions.config as config

ROWS, COLUMNS = config.map_settings["tile_height"], config.map_settings["tile_width"]
ZOOM_SCALE = config.map_settings["zoom"]
class MouseControls:
    def __init__(self, screen):
        self.screen = screen
        self.initX = 0
        self.initY = 0
        self.clicked = False
        self.dragging = False

    def left_click(self, event):
        self.clicked = True
        self.set_init(event)

    def left_click_up(self, event):
        self.dragging = False
        self.clicked = False

    def right_click(self, event):
        return
    
    def right_click_up(self, event):
        return
    
    def mouse_move(self, event):
        if self.clicked:
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

    def move_map(self, event):
        self.dragging = True
        config.map_settings["offsetX"] += event.pos[0] - self.initX
        config.map_settings["offsetY"] += event.pos[1] - self.initY
        self.initX = event.pos[0]
        self.initY = event.pos[1]

    def set_init(self, event):
        self.initX = event.pos[0]
        self.initY = event.pos[1]
    