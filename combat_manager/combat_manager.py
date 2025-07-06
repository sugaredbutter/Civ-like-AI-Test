import math
import random
import interactions.utils as utils
import combat_manager.combat_bonus_config as combat_bonus
class CombatManager:
    def combat(self, unit_1, unit_2, tile_1, tile_2, type):
        unit_1_combat_strength = unit_1.attack - (10 * (100 - unit_1.health)) / 100
        unit_2_combat_strength = unit_2.attack - (10 * (100 - unit_2.health)) / 100
        unit_2_combat_bonus = 0 
        if type == "melee":
            direction = utils.get_relative_position(tile_1.get_coords(), tile_2.get_coords())
            if direction != None and tile_1.rivers[direction] == True:
                unit_2_combat_bonus += combat_bonus.river["defensive_bonus"]
        unit_2_combat_bonus += combat_bonus.terrain.get(tile_2.terrain, {}).get("defensive_bonus", 0)
        unit_2_combat_bonus += combat_bonus.feature.get(tile_2.feature, {}).get("defensive_bonus", 0)


        unit_2_combat_strength += unit_2_combat_bonus
        print(unit_1_combat_strength, unit_2_combat_strength, unit_2_combat_bonus)
        


        unit_1_damage_dealt = 30*math.exp(.04*(unit_1_combat_strength - unit_2_combat_strength)) * random.uniform(0.8, 1.2)
        unit_1_damage_taken = 30*math.exp(.04*(unit_2_combat_strength - unit_1_combat_strength)) * random.uniform(0.8, 1.2)
        return (unit_1_damage_dealt, unit_1_damage_taken)
    
    def estimate_combat(self, unit_1, unit_2, tile_1, tile_2, type):
        unit_1_combat_strength = unit_1.attack - (10 * (100 - unit_1.health)) / 100
        unit_2_combat_strength = unit_2.attack - (10 * (100 - unit_2.health)) / 100
        unit_2_combat_bonus = 0 
        if type == "melee":
            direction = utils.get_relative_position(tile_1.get_coords(), tile_2.get_coords())
            if direction != None and tile_1.rivers[direction] == True:
                unit_2_combat_bonus += combat_bonus.river["defensive_bonus"]
        unit_2_combat_bonus += combat_bonus.terrain.get(tile_2.terrain, {}).get("defensive_bonus", 0)
        unit_2_combat_bonus += combat_bonus.feature.get(tile_2.feature, {}).get("defensive_bonus", 0)


        unit_2_combat_strength += unit_2_combat_bonus
        print(unit_1_combat_strength, unit_2_combat_strength, unit_2_combat_bonus)
        


        unit_1_damage_dealt = 30*math.exp(.04*(unit_1_combat_strength - unit_2_combat_strength))
        unit_1_damage_taken = 30*math.exp(.04*(unit_2_combat_strength - unit_1_combat_strength))
        return (unit_1_damage_dealt, unit_1_damage_taken)