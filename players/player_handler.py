import players.units_config as UnitConfig


class Player:
    def __init__(self, id, color, generated_map, unit_handler):
        self.id = id
        self.color = color
        self.generated_map = generated_map
        self.unit_handler = unit_handler
        self.units = []
        self.AI = False
        
        self.visible_tiles = set()
        self.revealed_tiles = set()
    
    def place_unit(self, unit_type, x, y, z):
        new_unit = self.unit_handler.add_unit(self.id, unit_type, (x, y, z))
        self.units.append(new_unit)
        self.generated_map.get_tile_hex(x, y, z).unit_id = new_unit
        return new_unit
    
    def remove_unit(self, unit_id):
        if unit_id in self.units:
            self.units.remove(unit_id)
            self.unit_handler.remove_unit(unit_id)
            return True
        return False
    
    def remove_all_units(self):
        for unit in self.units:
            self.unit_handler.remove_unit(unit)
        self.units.clear()
        
    def update_visibility(self):
        self.visible_tiles = set()
        for unit_id in self.units:
            unit = self.unit_handler.get_unit(unit_id)
            unit_visible = unit.get_visibility()
            self.visible_tiles.update(unit_visible)
            self.visible_tiles.add(unit.coord)
        self.revealed_tiles.update(self.visible_tiles)
    
    
class PlayerHandler:
    def __init__(self, generated_map, unit_handler):
        self.generated_map = generated_map
        self.unit_handler = unit_handler
        self.colors = [
            "red",   
            "blue",  
            "green",  
            "purple"  
        ]
        self.players = []

    def add_player(self):
        self.players.append(Player(len(self.players), self.colors[len(self.players)], self.generated_map, self.unit_handler))

    def get_player(self, id):
        return self.players[id]

    def remove_player(self):
        self.players[-1].remove_all_units()
        del self.players[-1]

    def end_game_reset(self):
        for players in self.players:
            players.revealed_tiles = set()
    