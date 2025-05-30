import players.units_config as UnitConfig


class Player:
    def __init__(self, id, color, generated_map, unit_handler):
        self.id = id
        self.color = color
        self.generated_map = generated_map
        self.unit_handler = unit_handler
        self.units = []
    
    def place_unit(self, unit_type, x, y, z):
        new_unit = self.unit_handler.add_unit(self.id, unit_type, UnitConfig.units[unit_type]["health"], (x, y, z))
        self.units.append(new_unit)
        self.generated_map.get_tile_hex(x, y, z).unit_id = new_unit
        return new_unit
    
    def remove_unit(self, unit_id):
        if unit_id in self.units:
            self.units.remove(unit_id)
            self.unit_handler.remove_unit(unit_id)
            print(len(self.units))
            return True
        return False
    
class PlayerHandler:
    def __init__(self, generated_map, unit_handler):
        self.generated_map = generated_map
        self.unit_handler = unit_handler

        self.players = []

    def add_player(self, color):
        self.players.append(Player(len(self.players), color, self.generated_map, self.unit_handler))

    def get_player(self, id):
        return self.players[id]

    def remove_player(self):
        del self.players[-1]
    