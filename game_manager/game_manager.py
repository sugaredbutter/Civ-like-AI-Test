import interactions.config as config
import game_manager.turn_manager as turn_manager
class GameManager:
    def __init__(self, players, units, generated_map):
        self.type = None
        self.players = players
        self.units = units
        self.generated_map = generated_map
        self.turn_manager = turn_manager.TurnManager(players, units, generated_map)
        
        self.game_types = ["Test", "PvAI, AIvAI"]
                
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
        
        
# To DO:
# Test:
# Turn Management
# Choose Player
# Next Turn button
# Move Units