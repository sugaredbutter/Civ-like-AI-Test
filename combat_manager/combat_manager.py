import math
import random
import utils as utils
import combat_manager.combat_bonus_config as combat_bonus
import units.units_config as unit_config
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
        
        if unit_2.type == "Ranged" and type == "melee":
            unit_2_combat_strength -= round(unit_2_combat_strength * unit_config.units[unit_2.type]["melee_attack_defensive_debuff"])


        try:
            unit_1_damage_dealt = 30*math.exp(.04*(unit_1_combat_strength - unit_2_combat_strength)) * random.uniform(0.8, 1.2)
            unit_1_damage_taken = 30*math.exp(.04*(unit_2_combat_strength - unit_1_combat_strength)) * random.uniform(0.8, 1.2)
        except OverflowError:
            print("Combat")
            print("Unit 1 CS:", unit_1_combat_strength, "Unit 2 CS:", unit_2_combat_strength)
            print("Unit 1 HP:", unit_1.health, "Unit 2 HP:", unit_2.health)
            return (0, 0)
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
        
        if unit_2.type == "Ranged" and type == "melee":
            unit_2_combat_strength -= round(unit_2_combat_strength * unit_config.units[unit_2.type]["melee_attack_defensive_debuff"])
        try:
            unit_1_damage_dealt = 30*math.exp(.04*(unit_1_combat_strength - unit_2_combat_strength))
            unit_1_damage_taken = 30*math.exp(.04*(unit_2_combat_strength - unit_1_combat_strength))
        except OverflowError:
            print("Estimate Combat")
            print("Unit 1 CS:", unit_1_combat_strength, "Unit 2 CS:", unit_2_combat_strength)
            print("Unit 1 HP:", unit_1.health, "Unit 2 HP:", unit_2.health)
            return (0, 0)
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
        
        if unit_2.type == "Ranged" and type == "melee":
            unit_2_combat_strength -= round(unit_2_combat_strength * unit_config.units[unit_2.type]["melee_attack_defensive_debuff"])


        return (unit_1_combat_strength, unit_2_combat_strength)
    
    def get_combat_bonus(unit_1, unit_2, tile_1, tile_2, type):
        unit_1_combat_bonuses = {
            "Health": -round((10 * (100 - unit_1.health)) / 100),
            "Terrain": 0,
            "Feature": 0,
            "River": 0,
            "Flanking": 0,
            "Fortified": 0,
            "Debuff": 0,
        }
        unit_2_combat_bonuses = {
            "Health": -round((10 * (100 - unit_2.health)) / 100),
            "Terrain": 0,
            "Feature": 0,
            "River": 0,
            "Flanking": 0,
            "Fortified": 0,
            "Debuff": 0,
        }
        unit_1_combat_strength = round(unit_1.attack - (10 * (100 - unit_1.health)) / 100)
        unit_2_combat_strength = round(unit_2.defense - (10 * (100 - unit_2.health)) / 100)
        unit_2_combat_bonus = 0 
        if type == "melee":
            direction = utils.get_relative_position(tile_1.get_coords(), tile_2.get_coords())
            if direction != None and tile_1.rivers[direction] == True:
                unit_2_combat_bonuses["River"] = combat_bonus.river["defensive_bonus"]
                unit_2_combat_bonus += combat_bonus.river["defensive_bonus"]

        unit_2_combat_bonuses["Terrain"] = combat_bonus.terrain.get(tile_2.terrain, {}).get("defensive_bonus", 0)
        unit_2_combat_bonuses["Feature"] = combat_bonus.feature.get(tile_2.feature, {}).get("defensive_bonus", 0)
        unit_2_combat_bonus += combat_bonus.terrain.get(tile_2.terrain, {}).get("defensive_bonus", 0)
        unit_2_combat_bonus += combat_bonus.feature.get(tile_2.feature, {}).get("defensive_bonus", 0)
        if unit_2.fortified:
            unit_2_combat_bonuses["Fortified"] = unit_config.units[unit_2.type]["fortified"]
            unit_2_combat_bonus += unit_config.units[unit_2.type]["fortified"]

            if unit_2.turns_fortified >= 1:
                unit_2_combat_bonuses["Fortified"] *= 2
                unit_2_combat_bonus += unit_config.units[unit_2.type]["fortified"]

        unit_2_combat_strength += unit_2_combat_bonus

        if unit_2.type == "Ranged" and type == "melee":
            unit_2_combat_bonuses["Debuff"] = -round(unit_config.units[unit_2.type]["melee_attack_defensive_debuff"] * unit_2_combat_strength)


        return unit_1_combat_bonuses, unit_2_combat_bonuses

    def get_offensive_CS(unit):
        unit_1_combat_strength = round(unit.attack - (10 * (100 - unit.health)) / 100)
        return unit_1_combat_strength
    
    def combat_death_probability(unit_1, unit_2, tile_1, tile_2, combat_type):
        # Compute combat strengths
        unit_1_combat_strength = unit_1.attack - round((10 * (100 - unit_1.health)) / 100)
        unit_2_combat_strength = unit_2.defense - round((10 * (100 - unit_2.health)) / 100)
        
        unit_2_combat_bonus = 0
        if type == "melee":
            direction = utils.get_relative_position(tile_1.get_coords(), tile_2.get_coords())
            if direction is not None and tile_1.rivers[direction]:
                unit_2_combat_bonus += combat_bonus.river["defensive_bonus"]
        unit_2_combat_bonus += combat_bonus.terrain.get(tile_2.terrain, {}).get("defensive_bonus", 0)
        unit_2_combat_bonus += combat_bonus.feature.get(tile_2.feature, {}).get("defensive_bonus", 0)
        
        if unit_2.fortified:
            unit_2_combat_bonus += unit_config.units[unit_2.type]["fortified"]
            if unit_2.turns_fortified >= 1:
                unit_2_combat_bonus += unit_config.units[unit_2.type]["fortified"]
        
        unit_2_combat_strength += unit_2_combat_bonus
        
        if unit_2.type == "Ranged" and type == "melee":
            unit_2_combat_strength -= round(
                unit_2_combat_strength * unit_config.units[unit_2.type]["melee_attack_defensive_debuff"]
            )
        
        base_damage_1 = 30 * math.exp(0.04 * (unit_1_combat_strength - unit_2_combat_strength))
        base_damage_2 = 30 * math.exp(0.04 * (unit_2_combat_strength - unit_1_combat_strength))

        # Compute death probabilities using random.uniform(0.8,1.2)
        def death_prob(base_damage, health):
            threshold = health / base_damage
            if threshold <= 0.8:
                return 1.0  # Guaranteed death
            elif threshold >= 1.2:
                return 0.0  # Cannot die
            else:
                return (1.2 - threshold) / 0.4  # Linear interpolation

        p_unit_1_dies = death_prob(base_damage_2, unit_1.health)
        p_unit_2_dies = death_prob(base_damage_1, unit_2.health)

        return p_unit_1_dies, p_unit_2_dies