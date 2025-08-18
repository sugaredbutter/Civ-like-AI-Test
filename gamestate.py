import config
import map.map as generate_map
import units.units as unit_handler
import players.player_handler as player_handler
import interactions.visual_effects as visual_effects_manager
WIDTH, HEIGHT = config.map_settings["pixel_width"], config.map_settings["pixel_height"]
ROWS, COLUMNS = config.map_settings["tile_height"], config.map_settings["tile_width"]
class GameState:
    def __init__(self, screen = None):
        if screen:
            self.visual_effects = visual_effects_manager.VisualEffectHandler(screen)
        else:
            self.visual_effects = None
        self.players =  player_handler.PlayerHandler(self)

        self.units = unit_handler.UnitHandler(self.visual_effects, self)
        self.map = generate_map.HexMap(ROWS, COLUMNS)
        self.players.add_player()  # player 1
        self.players.add_player()  # player 2
        self.tile_attackable_by = None
        self.legal_moves_dict = None
        self.current_player = 0
        self.current_turn = 1
        self.kills = [0] * config.num_players
        self.winner = -1

    def start(self):
        self.current_player = 0
        self.current_turn = 1
        self.kills = [0] * config.num_players
        self.deaths = [0] * config.num_players
        self.remaining = [len(player.units) for player in self.players.players]

    def reset(self):
        self.map.end_game_reset()
        self.units.end_game_reset()
        self.players.end_game_reset()
        config.log_file = -1
        self.winner = -1

