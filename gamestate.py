class GameState:
    def __init__(self, players, units, map):
        self.players = players
        self.units = units
        self.map = map
        self.tile_attackable_by = None
        self.legal_moves_dict = None