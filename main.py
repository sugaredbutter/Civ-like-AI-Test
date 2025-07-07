import pygame
import map_generator.map_generator as generate_map
import interactions.draw_map as draw_map
import config as config
import interactions.utils as utils
import interactions.controls as controls
import interactions.user_interface as ui
import interactions.test_user_interface as test_ui
import players.units as unit_handler
import players.player_handler as player_handler
import game_manager.game_manager as game
import combat_manager.combat_manager as combat_manager
import interactions.visual_effects as visual_effects_manager
pygame.init()

WIDTH, HEIGHT = config.map_settings["pixel_width"], config.map_settings["pixel_height"]
ROWS, COLUMNS = config.map_settings["tile_height"], config.map_settings["tile_width"]
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hex Map")

BACKGROUND_COLOR = (255, 255, 255)  # White
generated_map = generate_map.HexMap(ROWS, COLUMNS)

combat = combat_manager.CombatManager()
visual_effects = visual_effects_manager.VisualEffectHandler(screen)
units = unit_handler.UnitHandler(generated_map, combat, visual_effects)
players = player_handler.PlayerHandler(generated_map, units)
units.player_handler = players
players.add_player()  # Red player
players.add_player()  # Red player
user_interface = ui.UserInterface(screen, generated_map, players, units)
test_user_interface = test_ui.UserInterface(screen, generated_map, players, units)
tile_click_controls = controls.TileClickControls(screen, user_interface, generated_map, players, units)
game_manager = game.GameManager(players, units, generated_map, test_user_interface)
test_user_interface.game_manager = game_manager
game_control_interface = ui.GameControlsInterface(screen, game_manager)

mouse_controls = controls.MouseControls(screen, user_interface, test_user_interface, generated_map, tile_click_controls, game_control_interface, game_manager)

map = draw_map.Map(screen, generated_map, players, units, game_manager)

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


    map.draw_tiles(WIDTH, HEIGHT)
    game_control_interface.create_menu()

    if game_manager.type == None:
        user_interface.active_menu.create_menu()
    if game_manager.type == "Test":
        test_user_interface.active_menu.create_menu()

    visual_effects.display_visuals()
    pygame.display.flip()
    
    delta_time = clock.tick(60) / 1000
    delta_time = max(0.001, min(0.1, delta_time))
    

pygame.quit()