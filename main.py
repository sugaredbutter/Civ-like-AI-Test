import pygame
import map_generator.map_generator as generate_map
import map_generator.draw_map as draw_map
import map_generator.config as config
pygame.init()

WIDTH, HEIGHT = 800, 600
dragging = False
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hex Map")

BACKGROUND_COLOR = (255, 255, 255)  # White
running = True
initX, initY = 0, 0
offsetX, offsetY = 0, 0
while running:
    screen.fill(BACKGROUND_COLOR)
    draw_map.draw_tiles(screen, WIDTH, HEIGHT)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 1 = left click
                mouse_pos = pygame.mouse.get_pos()  # (x, y) tuple
                print(f"Clicked at pixel position: {mouse_pos}")
                dragging = True
                initX, initY = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                config.map_settings["offsetX"] += event.pos[0] - initX
                config.map_settings["offsetY"] += event.pos[1] - initY
        



    pygame.display.flip()
    

pygame.quit()