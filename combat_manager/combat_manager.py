import math
import random
class CombatManager:
    def combat(self, unit_1, unit_2):
        unit_1_damage_taken = 30*math.exp(.04*unit_1.attack - unit_2.defense) * random.randint(8, 12)/10
        unit_2_damage_taken = 30*math.exp(.04*unit_2.attack - unit_1.defense) * random.randint(8, 12)/10
        return (unit_1_damage_taken, unit_2_damage_taken)