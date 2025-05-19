import pygame
import map_generator.map_generator as generate_map
import map_generator.draw_map as draw_map
pygame.init()

WIDTH, HEIGHT = 800, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hex Map")

BACKGROUND_COLOR = (255, 255, 255)  # White
running = True
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

    pygame.display.flip()
    

pygame.quit()