import pygame
import map_generator.map_generator as generate_map
import interactions.draw_map as draw_map
import interactions.config as config
import interactions.utils as utils
import interactions.controls as controls
import interactions.user_interface as ui
pygame.init()

WIDTH, HEIGHT = config.map_settings["pixel_width"], config.map_settings["pixel_height"]
ROWS, COLUMNS = config.map_settings["tile_height"], config.map_settings["tile_width"]
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hex Map")

BACKGROUND_COLOR = (255, 255, 255)  # White
generated_map = generate_map.HexMap(ROWS, COLUMNS)
map = draw_map.Map(screen)
user_interface = ui.UserInterface(screen)
mouse_controls = controls.MouseControls(screen, user_interface, map)
running = True
clicked = False
dragging = False

initX, initY = 0, 0
offsetX, offsetY = 0, 0
while running:
    screen.fill(BACKGROUND_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 1 = left click
                mouse_controls.left_click(event)
        elif event.type == pygame.MOUSEBUTTONUP:    
            mouse_controls.left_click_up(event)
        elif event.type == pygame.MOUSEMOTION:
            mouse_controls.mouse_move(event)
        elif event.type == pygame.MOUSEWHEEL:
            mouse_controls.zoom(event)


    map.draw_tiles(WIDTH, HEIGHT, generated_map)
    user_interface.painter(False)


    pygame.display.flip()
    

pygame.quit()