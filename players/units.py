class Unit:
    def __init__(self, owner_id, id, type, health, alive = True):
        self.owner_id = owner_id
        self.id = id
        self.type = type
        self.health = health
        self.alive = alive
    
class UnitHandler:
    def __init__(self):
        self.units = {}
        self.id_counter = 0

    def add_unit(self, owner, type, health):
        unit = Unit(owner, self.id_counter, type, health)
        self.units[unit.id] = unit
        self.id_counter += 1
        return unit.id

    def get_unit(self, id):
        return self.units.get(id, None)

    def remove_unit(self, id):
        if id in self.units:
            del self.units[id]
            print(len(self.units))

            return True
        return False
    
    