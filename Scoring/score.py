import Scoring.score_config as score_config
import utils as utils
import math
from units.units_utils import UnitUtils
from units.units_utils import UnitMove
from units.units_utils import UnitVisibility
from units.units_utils import UnitAttack
from units.units_utils import UnitScoringUtils
from units.units_utils import UnitMoveScoring
from combat_manager.combat_manager import CombatManager


class UnitMoveScore:
    def __init__(self, unit, target_coord, game_state):
        self.game_state = game_state
        self.unit = unit
        self.target_coord = target_coord
        self.target_tile = self.game_state.map.get_tile_hex(*target_coord)
        self.player = game_state.players.get_player(self.unit.owner_id)
        self.score = 0
        self.reachable_tiles = None
        
    def get_score(self):  #Get score
        self.offensive_score()
        self.defensive_score()
        self.distance_score()
        self.exploration_score()
        return self.score
        
    def exploration_score(self):    #Score for exploring new lands
        revealed_tiles = self.player.revealed_tiles
        visible_tiles = self.player.visible_tiles
        exploration_score = 0
        # Explore unrevealed tiles
        if self.target_coord not in revealed_tiles:
            exploration_score += score_config.moveScore["exp_unrevealed"]
        elif self.target_coord not in visible_tiles:
            exploration_score += score_config.moveScore["exp_nonvisible"]
        # Bonus for Path to org destination (prevents going back and forward between 2 target tiles)
        if self.target_coord == self.unit.destination:
            exploration_score += score_config.moveScore["exp_org_destination"]
        self.score += exploration_score


        
    # Offensive Behavior for Melee
    # + Number of attackable units 
    # + Average damage + max inflicted damage on units
    # + Adjacent Enemies (for melee specifically)
    # Health Multiplier so this behavior is tuned down when lower health

    # Offensive Behavior for Ranged
    # + Number of attackable units 
    # + Average damage + max inflicted damage on units
    # Health Multiplier so this behavior is tuned down when lower health

    def offensive_score(self):  #Offensive/more aggressive behavior
        offensive_score = 0
        if self.unit.combat_type == "melee":
            attackable_enemies = UnitMoveScoring.get_attackable_units(self.unit, self.target_coord, self.game_state)
            if len(attackable_enemies) > 0:
                # Number of attackable enemies
                offensive_score += math.log2(len(attackable_enemies) + 1) * score_config.moveScore["off_attackable_enemy_units"]
                
                # Attackable Units                
                average_damage_inflicted = 0
                most_damage_inflicted = 0
                for tile_coord in attackable_enemies:
                    enemy_tile = self.game_state.map.get_tile_hex(*tile_coord)

                    enemy_unit = self.game_state.units.get_unit(enemy_tile.unit_id)
                    if self.unit.type == "Ranged":
                        damage_inflicted, damage_taken = CombatManager.estimate_combat(self.unit, enemy_unit, self.target_tile, enemy_tile, "ranged")
                    else:
                        damage_inflicted, damage_taken = CombatManager.estimate_combat(self.unit, enemy_unit, self.target_tile, enemy_tile, "melee")
                    average_damage_inflicted += damage_inflicted
                    most_damage_inflicted = max(most_damage_inflicted, damage_inflicted)

                offensive_score += average_damage_inflicted + most_damage_inflicted
                adjacent_tiles = utils.adjacent_tiles(self.target_coord)

                # Adjacent Enemies
                num_adjacent_units = 0
                for tile_coord in adjacent_tiles:
                    adjacent_tile = self.game_state.map.get_tile_hex(*tile_coord)
                    if adjacent_tile != None and adjacent_tile.unit_id != None:
                        tile_unit = self.game_state.units.get_unit(adjacent_tile.unit_id)
                        if tile_unit.owner_id != self.unit.owner_id:
                            num_adjacent_units += 1
                if num_adjacent_units > 0:
                    offensive_score += math.log2(len(attackable_enemies) + 1) * score_config.moveScore["off_adj_enemy_units"]
                
        else:
            attackable_enemies = UnitMoveScoring.get_attackable_units(self.unit, self.target_coord, self.game_state)
            if len(attackable_enemies) > 0:

                # Attackable enemy (does not scale with more)
                offensive_score += score_config.moveScore["off_attackable_enemy_units"]
                
                # Attackable Units                
                average_damage_inflicted = 0
                most_damage_inflicted = 0
                for tile_coord in attackable_enemies:
                    enemy_tile = self.game_state.map.get_tile_hex(*tile_coord)

                    enemy_unit = self.game_state.units.get_unit(enemy_tile.unit_id)
                    if self.unit.type == "Ranged":
                        damage_inflicted, damage_taken = CombatManager.estimate_combat(self.unit, enemy_unit, self.target_tile, enemy_tile, "ranged")
                    else:
                        damage_inflicted, damage_taken = CombatManager.estimate_combat(self.unit, enemy_unit, self.target_tile, enemy_tile, "melee")
                    average_damage_inflicted += damage_inflicted
                    most_damage_inflicted = max(most_damage_inflicted, damage_inflicted)

                offensive_score += most_damage_inflicted
                adjacent_tiles = utils.adjacent_tiles(self.target_coord)

        # Health Multiplier
        unit_health_mult = score_config.moveScore["off_mult"] * ((self.unit.health - 50) / 50)
        offensive_score = offensive_score * unit_health_mult
        #print(self.target_coord, "Off", offensive_score, unit_health_mult)

        self.score += offensive_score

    

    # Defensive Behavior
    # + Number of Adjacent Friendlies 
    # - Enemy potential damage to unit at tile
    # + Retaliatory Damage from unit at tile
    # Health Multiplier so this behavior is tuned down when higher health

    def defensive_score(self):  #Defensive Behavior
        defensive_score = 0
        reachable_tiles = UnitUtils.BFS_movement(self.unit, self.unit.movement, self.game_state)
        self.reachable_tiles = reachable_tiles
        #Adjacent Friendlies
        for tile_coord in reachable_tiles:
            tile = self.game_state.map.get_tile_hex(*tile_coord)
            if tile.unit_id != None:
                tile_unit = self.game_state.units.get_unit(tile.unit_id)
                if tile_unit.owner_id == self.unit.owner_id:
                    defensive_score += score_config.moveScore["def_adjacent_friendlies"]

        #Enemy potential damage to unit at tile
        enemy_units = self.game_state.tile_attackable_by.get(self.target_coord, set())
        potential_damage_taken = 0
        potential_damage_inflicted = 0
        for enemy_unit_ids in enemy_units:
            enemy_unit = self.game_state.units.get_unit(enemy_unit_ids)
            enemy_tile = self.game_state.map.get_tile_hex(*enemy_unit.coord)
            current_tile = self.game_state.map.get_tile_hex(*self.target_coord)
            if self.unit.type == "Ranged":
                damage_inflicted, damage_taken = CombatManager.estimate_combat(enemy_unit, self.unit, enemy_tile, current_tile, "ranged")
            else:
                damage_inflicted, damage_taken = CombatManager.estimate_combat(enemy_unit, self.unit, enemy_tile, current_tile, "melee")
            potential_damage_taken += damage_inflicted
            potential_damage_inflicted += damage_taken

        #Potential Damage Taken
        defensive_score -= potential_damage_taken * score_config.moveScore["def_damage_taken_mult"]

        #Potential Damage inflicted back (good if in very defensible location)
        defensive_score += potential_damage_inflicted * score_config.moveScore["def_damage_inflicted_mult"]
        if self.unit.combat_type == "melee":
            # Health Multiplier
            unit_health_mult = score_config.moveScore["off_mult"] * ((100 - self.unit.health) / 50)
            defensive_score = defensive_score * unit_health_mult
            #print(self.target_coord, "Def", defensive_score, unit_health_mult)
        else:
            # Health Multiplier
            unit_health_mult = score_config.moveScore["off_mult"] * ((100 - self.unit.health + 25) / 50)
            defensive_score = defensive_score * unit_health_mult
        self.score += defensive_score


    def distance_score(self):   #Score for how far target is
        if self.target_coord in self.reachable_tiles:
            return
        a = self.unit.coord
        b = self.target_coord
        distance = max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2]))

        self.score = self.score * math.exp(-score_config.moveScore["dist_move_penalty_alpha"] * distance)

class UnitAttackScore:
    def __init__(self, unit, target_coord, game_state):
        self.game_state = game_state
        self.unit = unit
        self.unit_tile = self.game_state.map.get_tile_hex(*unit.coord)
        self.target_coord = target_coord
        self.target_tile = self.game_state.map.get_tile_hex(*target_coord)
        self.target_unit = self.game_state.units.get_unit(self.target_tile.unit_id)
        self.player = game_state.players.get_player(self.unit.owner_id)
        self.score = 0
        self.reachable_tiles = None

    def get_score(self):  #Get score
        self.combat_score()
        return self.score

    def combat_score(self):
        combat_score = 0
        if self.unit.combat_type == "melee":
            damage_inflicted, damage_taken = CombatManager.estimate_combat(self.unit, self.target_unit, self.unit_tile, self.target_tile, self.unit.combat_type)

            # Bonus for possibly killing enemy (> 50% chance)
            if self.target_unit.health - damage_inflicted <= 0:
                combat_score += score_config.attackScore["combat_kill_bonus"]

            # Penalty for possibly dying (> 50% chance)
            if self.unit.health - damage_taken <= 0:
                combat_score -= score_config.attackScore["combat_death_penalty"]

            combat_score += self.unit.health / 100 * score_config.attackScore["combat_health_aggro"]

            # Damage Inflicted vs Damage Taken ratio
            combat_score += (damage_inflicted - damage_taken) * score_config.attackScore["combat_damage_mult"]

            # Nearby Allies as support vs Enemies
            nearby_tiles = UnitScoringUtils.BFS_nearby_units(self.unit, self.unit.coord, 5, self.game_state)
            player_CS = 0
            enemy_CS = 0
            for tile_coord in nearby_tiles:
                tile = self.game_state.map.get_tile_hex(*tile_coord)
                if tile.unit_id != None:
                    unit = self.game_state.units.get_unit(tile.unit_id)
                    if unit.owner_id == self.unit.owner_id:
                        player_CS += CombatManager.get_offensive_CS(unit)
                    else:
                        enemy_CS += CombatManager.get_offensive_CS(unit)
            combat_score += player_CS * score_config.attackScore["combat_ally_bonus_mult_bonus"]
            combat_score -= enemy_CS * score_config.attackScore["combat_enemy_bonus_mult_penalty"]
            # Health Multiplier
            unit_health_mult = score_config.attackScore["combat_mult"] * ((self.unit.health ) / 50)
            combat_score = combat_score * unit_health_mult
            #print(self.target_coord, "Off", offensive_score, unit_health_mult)
            self.score += combat_score
            
            if self.unit.health - damage_taken <= 0:
                full_path = UnitUtils.A_star(self.unit, self.target_coord, self.game_state, False, True)
                current_player = self.game_state.players.get_player(self.unit.owner_id)
                revealed_tiles = current_player.revealed_tiles
                visibile_tiles = current_player.visible_tiles
                tile_before = None
                #Find next tile for unit to move to
                print(self.player.id, self.unit.coord, full_path)
                if self.target_coord in full_path:
                    movement_left = self.unit.remaining_movement
                    for x in range(len(full_path)):
                        tile = self.game_state.map.get_tile_hex(*full_path[x])
                        enter_ZOC = UnitUtils.zone_of_control(self.unit, tile.get_coords(), self.game_state)
                        if enter_ZOC and tile.get_coords() != self.unit.coord:
                            tile_before = tile.get_coords()
                            break
                        tile_before = tile.get_coords()
                        current_player.update_visibility()
                        
                        next_tile = self.game_state.map.get_tile_hex(*full_path[x + 1])
                        
                        if next_tile.get_coords() == self.target_coord:
                            tile_before = tile.get_coords()
                            break


                        direction = utils.get_relative_position(tile.get_coords(), next_tile.get_coords())
                        direction = utils.OPPOSITE_EDGES[direction]

                        
                        next_tile_movement = min(self.unit.movement, next_tile.get_movement(direction))
                        

                        
                        if movement_left - next_tile_movement < 0:
                            tile_before = tile.get_coords()
                            break
                        else:
                            movement_left -= next_tile_movement
                    if self.game_state.legal_moves_dict.get(tile_before, None) == None:
                        scorer = UnitMoveScore(self.unit, tile_before, self.game_state)
                        combat_score += scorer.get_score()
                    else:
                        combat_score += self.game_state.legal_moves_dict[tile_before].score
            else:
                scorer = UnitMoveScore(self.unit, self.target_coord, self.game_state)
                combat_score += scorer.get_score()
        else:
            damage_inflicted, damage_taken = CombatManager.estimate_combat(self.unit, self.target_unit, self.unit_tile, self.target_tile, self.unit.combat_type)

            # Bonus for possibly killing enemy (> 50% chance)
            if self.target_unit.health - damage_inflicted <= 0:
                combat_score += score_config.attackScore["combat_kill_bonus"]

            # Current tile's status
            if self.game_state.legal_moves_dict.get(self.unit.coord, None) == None:
                scorer = UnitMoveScore(self.unit, self.unit.coord, self.game_state)
                combat_score += scorer.get_score()
            else:
                combat_score += self.game_state.legal_moves_dict[self.unit.coord].score

            # Health Multiplier
            unit_health_mult = score_config.attackScore["combat_mult"] * ((self.unit.health ) / 50)
            combat_score = combat_score * unit_health_mult
            #print(self.target_coord, "Off", offensive_score, unit_health_mult)
            self.score += combat_score


class UnitFortifyScore:
    def __init__(self, unit, game_state):
        self.game_state = game_state
        self.unit = unit
        self.unit_tile = self.game_state.map.get_tile_hex(*unit.coord)
        self.player = game_state.players.get_player(self.unit.owner_id)
        self.score = 0
        self.reachable_tiles = None

    def get_score(self):  #Get score
        self.get_fortify_score()
        return self.score
    
    def get_fortify_score(self):
        fortify_score = 0

        # Current tile's status
        if self.game_state.legal_moves_dict.get(self.unit.coord, None) == None:
            scorer = UnitMoveScore(self.unit, self.unit.coord, self.game_state)
            fortify_score += scorer.get_score()
        else:
            fortify_score += self.game_state.legal_moves_dict[self.unit.coord].score
        if self.unit.fortified == True:
            fortify_score += score_config.fortifyScore["fortify_continued"]
        if self.unit.health < 100:
            fortify_score += score_config.fortifyScore["fortify_not_full"]
        else:
            fortify_score -= score_config.fortifyScore["fortify_full_penalty"]


        unit_health_mult = score_config.fortifyScore["fortify_mult"] * (0.25 + ((100 - self.unit.health) / 100) ** 2)
        fortify_score = fortify_score * unit_health_mult
        #print(self.target_coord, "Def", defensive_score, unit_health_mult)
        self.score += fortify_score
        

        