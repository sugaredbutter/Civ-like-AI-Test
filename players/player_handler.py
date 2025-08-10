import units.units_config as UnitConfig


class Player:
    def __init__(self, id, color, game_state):
        self.id = id
        self.color = color
        self.game_state = game_state
        self.units = []
        self.elim_units = []
        self.AI = False
        self.eliminated = False
        
        self.visible_tiles = set()
        self.revealed_tiles = set()
    
    def place_unit(self, unit_type, x, y, z):
        new_unit = self.game_state.units.add_unit(self.id, unit_type, (x, y, z))
        self.units.append(new_unit)
        self.game_state.map.get_tile_hex(x, y, z).unit_id = new_unit
        return new_unit
    
    def remove_unit(self, unit_id):
        if unit_id in self.units:
            self.units.remove(unit_id)
            self.game_state.units.remove_unit(unit_id)
            return True
        return False
    
    def remove_all_units(self):
        for unit in self.units:
            self.game_state.units.remove_unit(unit)
        self.units.clear()
        
    def update_visibility(self):
        self.visible_tiles = set()
        for unit_id in self.units:
            unit = self.game_state.units.get_unit(unit_id)
            if unit.alive == True:
                unit_visible = unit.get_visibility()
                self.visible_tiles.update(unit_visible)
                self.visible_tiles.add(unit.coord)
        self.revealed_tiles.update(self.visible_tiles)
    
    
class PlayerHandler:
    def __init__(self):
        self.game_state = None
        self.colors = [
            "red",   
            "blue",  
            "green",  
            "purple",  
        ]
        self.players = []

    def add_player(self):
        self.players.append(Player(len(self.players), self.colors[len(self.players)], self.game_state))

    def get_player(self, id):
        return self.players[id]

    def remove_player(self):
        self.players[-1].remove_all_units()
        del self.players[-1]

    def end_game_reset(self):
        for players in self.players:
            players.revealed_tiles = set()
            players.visible_tiles = set()
            players.eliminated = False
            players.elim_units = []

    def start_game(self, type):
        print("hi")
        if type == "Test":
            self.players[0].update_visibility()
            
        elif type == "PvAITest" or type == "PvAI":
            self.players[0].update_visibility()
            for x in range(1, len(self.players)):
                self.players[x].AI = True
        for x in self.players:
            print(x.AI)

    