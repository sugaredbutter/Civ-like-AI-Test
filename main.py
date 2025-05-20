import pygame
import map_generator.map_generator as generate_map
import map_generator.draw_map as draw_map
import map_generator.config as config
import interactions.interactions as interactions
pygame.init()

WIDTH, HEIGHT = 800, 600
ROWS, COLUMNS = 8, 8
ZOOM_SCALE = 5
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hex Map")

BACKGROUND_COLOR = (255, 255, 255)  # White
map = generate_map.HexMap(ROWS, COLUMNS)


running = True
clicked = False
dragging = False

initX, initY = 0, 0
offsetX, offsetY = 0, 0
while running:
    screen.fill(BACKGROUND_COLOR)
    draw_map.draw_tiles(screen, WIDTH, HEIGHT, map)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 1 = left click
                mouse_pos = pygame.mouse.get_pos()  # (x, y) tuple
                print(f"Clicked at pixel position: {mouse_pos}")
                clicked = True
                initX, initY = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
            clicked = False
        elif event.type == pygame.MOUSEMOTION:
            if clicked:
                dragging = True
                config.map_settings["offsetX"] += event.pos[0] - initX
                config.map_settings["offsetY"] += event.pos[1] - initY
                initX = event.pos[0]
                initY = event.pos[1]
        elif event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()
            if event.y > 0 and config.hex["radius"] < 250:
                config.hex["radius"] += 5
                config.map_settings["offsetX"] -= ZOOM_SCALE * COLUMNS
                config.map_settings["offsetY"] += ZOOM_SCALE * ROWS
            elif event.y < 0 and config.hex["radius"] > 10:
                config.hex["radius"] -= 5
                config.map_settings["offsetX"] += ZOOM_SCALE * COLUMNS
                config.map_settings["offsetY"] -= ZOOM_SCALE * ROWS


        



    pygame.display.flip()
    

pygame.quit()