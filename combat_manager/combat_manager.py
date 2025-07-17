import math
import random
import utils as utils
import combat_manager.combat_bonus_config as combat_bonus
import players.units_config as unit_config
class CombatManager:
    def combat(unit_1, unit_2, tile_1, tile_2, type):
        unit_1_combat_strength = unit_1.attack - round((10 * (100 - unit_1.health)) / 100)
        unit_2_combat_strength = unit_2.defense - round((10 * (100 - unit_2.health)) / 100)
        unit_2_combat_bonus = 0 
        if type == "melee":
            direction = utils.get_relative_position(tile_1.get_coords(), tile_2.get_coords())
            if direction != None and tile_1.rivers[direction] == True:
                unit_2_combat_bonus += combat_bonus.river["defensive_bonus"]
        unit_2_combat_bonus += combat_bonus.terrain.get(tile_2.terrain, {}).get("defensive_bonus", 0)
        unit_2_combat_bonus += combat_bonus.feature.get(tile_2.feature, {}).get("defensive_bonus", 0)
        if unit_2.fortified:
            unit_2_combat_bonus += unit_config.units[unit_2.type]["fortified"]
            if unit_2.turns_fortified >= 1:
                unit_2_combat_bonus += unit_config.units[unit_2.type]["fortified"]

        unit_2_combat_strength += unit_2_combat_bonus
        


        unit_1_damage_dealt = 30*math.exp(.04*(unit_1_combat_strength - unit_2_combat_strength)) * random.uniform(0.8, 1.2)
        unit_1_damage_taken = 30*math.exp(.04*(unit_2_combat_strength - unit_1_combat_strength)) * random.uniform(0.8, 1.2)
        return (unit_1_damage_dealt, unit_1_damage_taken)
    
    def estimate_combat(unit_1, unit_2, tile_1, tile_2, type):
        unit_1_combat_strength = unit_1.attack - round((10 * (100 - unit_1.health)) / 100)
        unit_2_combat_strength = unit_2.defense - round((10 * (100 - unit_2.health)) / 100)
        unit_2_combat_bonus = 0 
        if type == "melee":
            direction = utils.get_relative_position(tile_1.get_coords(), tile_2.get_coords())
            if direction != None and tile_1.rivers[direction] == True:
                unit_2_combat_bonus += combat_bonus.river["defensive_bonus"]
        unit_2_combat_bonus += combat_bonus.terrain.get(tile_2.terrain, {}).get("defensive_bonus", 0)
        unit_2_combat_bonus += combat_bonus.feature.get(tile_2.feature, {}).get("defensive_bonus", 0)
        if unit_2.fortified:
            unit_2_combat_bonus += unit_config.units[unit_2.type]["fortified"]
            if unit_2.turns_fortified >= 1:
                unit_2_combat_bonus += unit_config.units[unit_2.type]["fortified"]

        unit_2_combat_strength += unit_2_combat_bonus
        


        unit_1_damage_dealt = 30*math.exp(.04*(unit_1_combat_strength - unit_2_combat_strength))
        unit_1_damage_taken = 30*math.exp(.04*(unit_2_combat_strength - unit_1_combat_strength))
        return (unit_1_damage_dealt, unit_1_damage_taken)
    
    def get_combat_strength(unit_1, unit_2, tile_1, tile_2, type):
        unit_1_combat_strength = round(unit_1.attack - (10 * (100 - unit_1.health)) / 100)
        unit_2_combat_strength = round(unit_2.defense - (10 * (100 - unit_2.health)) / 100)
        unit_2_combat_bonus = 0 
        if type == "melee":
            direction = utils.get_relative_position(tile_1.get_coords(), tile_2.get_coords())
            if direction != None and tile_1.rivers[direction] == True:
                unit_2_combat_bonus += combat_bonus.river["defensive_bonus"]
        unit_2_combat_bonus += combat_bonus.terrain.get(tile_2.terrain, {}).get("defensive_bonus", 0)
        unit_2_combat_bonus += combat_bonus.feature.get(tile_2.feature, {}).get("defensive_bonus", 0)
        if unit_2.fortified:
            unit_2_combat_bonus += unit_config.units[unit_2.type]["fortified"]
            if unit_2.turns_fortified >= 1:
                unit_2_combat_bonus += unit_config.units[unit_2.type]["fortified"]

        unit_2_combat_strength += unit_2_combat_bonus
        
        return (unit_1_combat_strength, unit_2_combat_strength)
    
    def get_combat_bonus(unit_1, unit_2, tile_1, tile_2, type):
        unit_1_combat_bonuses = {
            "Health": -round((10 * (100 - unit_1.health)) / 100),
            "Terrain": 0,
            "Feature": 0,
            "River": 0,
            "Flanking": 0,
            "Fortified": 0,
        }
        unit_2_combat_bonuses = {
            "Health": -round((10 * (100 - unit_2.health)) / 100),
            "Terrain": 0,
            "Feature": 0,
            "River": 0,
            "Flanking": 0,
            "Fortified": 0,
        }
        if type == "melee":
            direction = utils.get_relative_position(tile_1.get_coords(), tile_2.get_coords())
            if direction != None and tile_1.rivers[direction] == True:
                unit_2_combat_bonuses["River"] = combat_bonus.river["defensive_bonus"]
        unit_2_combat_bonuses["Terrain"] = combat_bonus.terrain.get(tile_2.terrain, {}).get("defensive_bonus", 0)
        unit_2_combat_bonuses["Feature"] = combat_bonus.feature.get(tile_2.feature, {}).get("defensive_bonus", 0)
        if unit_2.fortified:
            unit_2_combat_bonuses["Fortified"] = unit_config.units[unit_2.type]["fortified"]
            if unit_2.turns_fortified >= 1:
                unit_2_combat_bonuses["Fortified"] *= 2
        return unit_1_combat_bonuses, unit_2_combat_bonuses
