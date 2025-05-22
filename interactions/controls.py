import pygame
import interactions.config as config
import interactions.utils as utils

ROWS, COLUMNS = config.map_settings["tile_height"], config.map_settings["tile_width"]
ZOOM_SCALE = config.map_settings["zoom"]
class MouseControls:
    def __init__(self, screen, user_interface, map, generated_map):
        self.screen = screen
        self.user_interface = user_interface
        self.map = map
        self.generated_map = generated_map
        self.initX = 0
        self.initY = 0
        self.clicked = False
        self.dragging = False
        self.clicked_button = False

    def left_click(self, event):
        self.clicked = True
        if self.user_interface.is_clicked(event):
            self.clicked_button = True
            print("yeah")
        elif self.user_interface.active_button != None:
            self.user_interface.paint_biome(self.generated_map)
        self.set_init(event)

    def left_click_up(self, event):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if self.clicked_button and self.user_interface.is_clicked(event):
            self.user_interface.button_clicked()   
        #elif self.dragging == False and self.generated_map.get_tile(utils.click_to_hex(mouse_x, mouse_y)) != False:

        self.dragging = False
        self.clicked = False
        self.clicked_button = False
        self.user_interface.valid_hover = True

    def right_click(self, event):
        return
    
    def right_click_up(self, event):
        return
    
    def mouse_move(self, event):
        if self.clicked and not self.clicked_button:
            self.user_interface.valid_hover = False
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
        if self.user_interface.active_button != None:
            self.user_interface.paint_biome(self.generated_map)
        else:
            self.dragging = True
            config.map_settings["offsetX"] += event.pos[0] - self.initX
            config.map_settings["offsetY"] += event.pos[1] - self.initY
            self.initX = event.pos[0]
            self.initY = event.pos[1]

    def set_init(self, event):
        self.initX = event.pos[0]
        self.initY = event.pos[1]
    