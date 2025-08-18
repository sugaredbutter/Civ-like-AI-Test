import pygame
import sys
import interactions.draw_map as draw_map
import config as config
import utils as utils
import interactions.controls as controls
import interactions.interfaces.user_interface as ui
import interactions.interfaces.test_user_interface as test_ui
import interactions.interfaces.player_v_AI_interface as pvAI_ui
import interactions.interfaces.player_v_AI_test_interface as pvAI_test_ui
import interactions.interfaces.interfaces as interfaces

import interactions.interfaces.game_interface as game_ui
import game_manager.game_manager as game
import gamestate as gamestate


WIDTH, HEIGHT = config.map_settings["pixel_width"], config.map_settings["pixel_height"]
ROWS, COLUMNS = config.map_settings["tile_height"], config.map_settings["tile_width"]

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hex Map")

BACKGROUND_COLOR = (255, 255, 255)  # White

game_state = gamestate.GameState(screen)


user_interface = ui.UserInterface(screen, game_state)
test_user_interface = test_ui.UserInterface(screen, game_state)
player_v_AI_interface = pvAI_ui.UserInterface(screen, game_state)
player_v_AI_test_interface = pvAI_test_ui.UserInterface(screen, game_state)
game_control_interface = game_ui.GameControlsInterface(screen)

all_interfaces = interfaces.Interfaces(game_control_interface, user_interface, test_user_interface, player_v_AI_test_interface, player_v_AI_interface)

game_manager = game.GameManager(screen, game_state, all_interfaces)
test_user_interface.set_game_manager(game_manager)
player_v_AI_interface.set_game_manager(game_manager)
player_v_AI_test_interface.set_game_manager(game_manager)
game_control_interface.set_game_manager(game_manager)
mouse_controls = controls.MouseControls(screen, game_state, game_control_interface, game_manager, all_interfaces)

map = draw_map.Map(screen, game_state)

running = True
clicked = False
dragging = False

initX, initY = 0, 0
offsetX, offsetY = 0, 0
clock = pygame.time.Clock()
delta_time = 0.1
x = 0


while running:
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
    if game_manager.type != "Start":
        game_control_interface.create_menu()
    else:
        game_control_interface.active_menu.create_menu()
    if game_manager.type == None:
        user_interface.active_menu.create_menu()
    elif game_manager.type == "Test":
        test_user_interface.active_menu.create_menu()
    elif game_manager.type == "PvAITest":
        player_v_AI_test_interface.active_menu.create_menu()

    game_state.visual_effects.display_visuals()
    pygame.display.flip()
    
    delta_time = clock.tick(60) / 1000
    delta_time = max(0.001, min(0.1, delta_time))
    

pygame.quit()
sys.exit()