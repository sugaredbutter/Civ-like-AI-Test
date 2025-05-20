import pygame
import map_generator.map_generator as generate_map
import map_generator.draw_map as draw_map
import interactions.config as config
import interactions.utils as utils
import interactions.controls as controls
pygame.init()

WIDTH, HEIGHT = config.map_settings["pixel_width"], config.map_settings["pixel_height"]
ROWS, COLUMNS = config.map_settings["tile_height"], config.map_settings["tile_width"]
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hex Map")

BACKGROUND_COLOR = (255, 255, 255)  # White
map = generate_map.HexMap(ROWS, COLUMNS)
mouse_controls = controls.mouse_controls(screen)

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
                clicked = True
                mouse_controls.set_init(event)
        elif event.type == pygame.MOUSEBUTTONUP:    
            dragging = False
            clicked = False
        elif event.type == pygame.MOUSEMOTION:
            if clicked:
                dragging = True
                mouse_controls.move_map(event)
        elif event.type == pygame.MOUSEWHEEL:
            mouse_controls.zoom(event)


    draw_map.draw_tiles(screen, WIDTH, HEIGHT, map)




    pygame.display.flip()
    

pygame.quit()