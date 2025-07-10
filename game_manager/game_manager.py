import config as config
import game_manager.turn_manager as turn_manager
import interactions.utils as utils
class GameManager:
    def __init__(self, screen, players, units, generated_map, test_user_interface):
        self.type = None
        self.screen = screen
        self.players = players
        self.units = units
        self.generated_map = generated_map
        self.test_user_interface = test_user_interface
        self.turn_manager = turn_manager.TurnManager(players, units, generated_map)
        
        self.game_types = ["Test", "PvAI, AIvAI"]
        self.current_player = 0
                
    def start_game(self, game_type):
        print("Attempting to start game of type:", game_type)
        if self.start_game_check(game_type) == False:
            print("Game start check failed for type:", game_type)
            return False
        self.type = game_type
        self.turn_manager.in_game = True
        self.turn_manager.current_turn = 0
        self.turn_manager.current_player = 0
        print("Game started successfully with type:", game_type)
        config.game_type = game_type
        current_player = self.players.get_player(self.current_player)
        current_player.update_visibility()
        self.generated_map.start_game()
        return True

    def start_game_check(self, game_type):
        if game_type == "Test":
            return True
        elif game_type == "PvAI":
            num_players = config.num_players
            for x in range(num_players):
                player = self.players.get_player(x)
                if len(player.units) == 0:
                    return False
        elif game_type == "AIvAI":
            num_players = config.num_players
            for x in range(num_players):
                player = self.players.get_player(x)
                if len(player.units) == 0:
                    return False
        
        return True
    
    def end_game(self):
        print("Ending game of type:", self.type)
        self.type = None
        self.turn_manager.in_game = False
        self.turn_manager.current_turn = 0
        self.turn_manager.current_player = 0
        self.generated_map.end_game_reset()
        self.units.end_game_reset()
        self.test_user_interface.end_game_reset()
        self.current_player = 0
        self.players.end_game_reset()
        config.game_type = None
        
    def next_turn(self):
        current_player = self.players.get_player(self.current_player)

        for unit_id in current_player.units:
            self.units.get_unit(unit_id).end_turn()
        current_player.update_visibility()
        if self.current_player >= len(self.players.players) - 1:
            self.current_player = 0
        else:
            self.current_player += 1
            
        current_player = self.players.get_player(self.current_player)
        for unit in current_player.units:
            self.units.get_unit(unit).turn_begin()
        current_player.update_visibility()

        self.test_user_interface.update_UI(self.current_player)
        
    def cycle_unit(self):
        current_player = self.players.get_player(self.current_player)

        for unit_id in current_player.units:
            unit = self.units.get_unit(unit_id)
            if unit.action:
                tile = self.generated_map.get_tile_hex(*unit.coord)
                utils.move_screen_to_tile(tile, self.screen)
                return (tile, unit)
        return None

            
        
# To DO:
# Test:
# Turn Management
# Choose Player
# Next Turn button
# Move Units