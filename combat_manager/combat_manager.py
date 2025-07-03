import math
import random
class CombatManager:
    def combat(self, unit_1, unit_2):
        unit_1_damage_dealt = 30*math.exp(.04*(unit_1.attack - unit_2.defense)) * random.randint(8, 12)/10
        unit_1_damage_taken = 30*math.exp(.04*(unit_2.defense - unit_1.attack)) * random.randint(8, 12)/10
        return (unit_1_damage_dealt, unit_1_damage_taken)