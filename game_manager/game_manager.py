import config as config
import psutil, os
import game_manager.turn_manager as turn_manager
import utils as utils
from Agents.agent import ScoreAgent 
class GameManager:
    def __init__(self, screen, game_state, interfaces):
        self.type = None
        self.screen = screen
        self.game_state = game_state
        self.interfaces = interfaces
        
        self.game_types = ["Test", "PvAITest", "AIvAITest", "PvAI, AIvAI"]
        self.current_player = 0
                
    def setup(self):
        self.type = "Start"
        config.game_type = "Start"

    def start_game(self, game_type):
        print("Attempting to start game of type:", game_type)
        if self.start_game_check(game_type) == False:
            print("Game start check failed for type:", game_type)
            self.end_game()
            return False
        self.type = game_type
        print("Game started successfully with type:", game_type)
        config.game_type = game_type
        self.game_state.players.start_game(game_type)
        self.game_state.map.start_game()
        return True

    def start_game_check(self, game_type):
        if game_type == "Test":
            return True
        elif game_type == "PvAI" or game_type == "PvAITest":
            num_players = config.num_players
            for x in range(num_players):
                player = self.game_state.players.get_player(x)
                if len(player.units) == 0:
                    return False
        elif game_type == "AIvAI":
            num_players = config.num_players
            for x in range(num_players):
                player = self.game_state.players.get_player(x)
                if len(player.units) == 0:
                    return False
        
        return True
    
    def end_game(self):
        print("Ending game of type:", self.type)
        self.type = None
        self.game_state.map.end_game_reset()
        self.game_state.units.end_game_reset()
        self.interfaces.test_user_interface.end_game_reset()
        self.interfaces.player_v_AI_interface.end_game_reset()
        self.interfaces.player_v_AI_test_interface.end_game_reset()
        self.current_player = 0
        self.game_state.players.end_game_reset()
        self.interfaces.game_control_interface.active_button = "Start"
        config.game_type = None
        
    def next_turn(self):
        if self.type == "Test":
            current_player = self.game_state.players.get_player(self.current_player)

            for unit_id in current_player.units:
                self.game_state.units.get_unit(unit_id).end_turn()
            current_player.update_visibility()
            if self.current_player >= len(self.game_state.players.players) - 1:
                self.current_player = 0
            else:
                self.current_player += 1
                
            current_player = self.game_state.players.get_player(self.current_player)
            while current_player.eliminated:
                if self.current_player >= len(self.game_state.players.players) - 1:
                    self.current_player = 0
                else:
                    self.current_player += 1
                current_player = self.game_state.players.get_player(self.current_player)
            for unit in current_player.units:
                self.game_state.units.get_unit(unit).turn_begin()
            current_player.update_visibility()

            self.interfaces.test_user_interface.update_UI(self.current_player)
        elif self.type == "PvAITest":
            current_player = self.game_state.players.get_player(self.current_player)

            for unit_id in current_player.units:
                self.game_state.units.get_unit(unit_id).end_turn()
            current_player.update_visibility()
            if self.current_player >= len(self.game_state.players.players) - 1:
                self.current_player = 0
            else:
                self.current_player += 1
            current_player = self.game_state.players.get_player(self.current_player)
            while current_player.eliminated:
                if self.current_player >= len(self.game_state.players.players) - 1:
                    self.current_player = 0
                else:
                    self.current_player += 1
                current_player = self.game_state.players.get_player(self.current_player)
            for unit in current_player.units:
                self.game_state.units.get_unit(unit).turn_begin()
            current_player.update_visibility()

            self.interfaces.player_v_AI_test_interface.update_UI(self.current_player)
            print("game_man", self.current_player)
            #if current_player.AI:
            #    ScoreAgent.choose_best_actions(self.current_player, self.game_state)
            #    self.next_turn()
        process = psutil.Process(os.getpid())
        print("Memory (MB):", process.memory_info().rss / (1024 * 1024))
    def cycle_unit(self):
        current_player = self.game_state.players.get_player(self.current_player)

        for unit_id in current_player.units:
            unit = self.game_state.units.get_unit(unit_id)
            if unit.action and unit.alive:
                tile = self.game_state.map.get_tile_hex(*unit.coord)
                utils.move_screen_to_tile(tile, self.screen)
                return (tile, unit)
        return None
    
    def check_win(self):
        num_players = len(self.game_state.players.players)
        num_alive = 0
        for player_id in range(num_players):
            current_player = self.game_state.players.get_player(player_id)
            if len(current_player.elim_units) >= len(current_player.units):
                current_player.eliminated = True
            if current_player.eliminated == False:
                num_alive += 1
        print(num_alive)
        if num_alive <= 1:
            self.end_game()





            
        
# To DO:
# Test:
# Turn Management
# Choose Player
# Next Turn button
# Move Units