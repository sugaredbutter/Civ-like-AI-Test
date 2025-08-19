import pygame
import sys
import map.map as generate_map
import interactions.draw_map as draw_map
import config as config
import utils as utils
import replays.replay_controls as replay_controls
import replays.replay_manager as replay_manager

import units.units as unit_handler
import players.player_handler as player_handler

import interactions.visual_effects as visual_effects_manager
import gamestate as gamestate

import time

pygame.init()

WIDTH, HEIGHT = config.map_settings["pixel_width"], config.map_settings["pixel_height"]
ROWS, COLUMNS = config.map_settings["tile_height"], config.map_settings["tile_width"]
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hex Map")

BACKGROUND_COLOR = (255, 255, 255)  # White

game_state = gamestate.GameState(screen)
mouse_controls = replay_controls.MouseControls(screen, game_state)
map = draw_map.Map(screen, game_state)
replay = replay_manager.ReplayManager(game_state)

start_time = 0

file_num = ""
while True:
    file_num = input("Enter # representing log file you want to replay (Ex: 1). Type q to quit.: ")
    if file_num == "q":
        break
    setup = replay.setup(file_num)
    start_time = time.time()
    if setup == False:
        continue


    running = True
    clicked = False
    dragging = False

    initX, initY = 0, 0
    offsetX, offsetY = 0, 0
    clock = pygame.time.Clock()
    delta_time = 0.1
    x = 0

    start = time.time()
    while running:
        if time.time() - start_time >= .5:
            replay.complete_next_action()
            start_time = time.time()
        screen.fill(BACKGROUND_COLOR)
        x += 50 * delta_time

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
            elif event.type == pygame.KEYDOWN:
                mouse_controls.key_down(event)
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


        map.draw_tiles()

        game_state.visual_effects.display_visuals()
        pygame.display.flip()
        
        delta_time = clock.tick(60) / 1000
        delta_time = max(0.001, min(0.1, delta_time))
        

pygame.quit()
sys.exit()