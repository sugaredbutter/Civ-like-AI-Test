import utils as utils
import units.units_config as units_config
import heapq
from collections import deque
import map.tile_types_config as tile_config
import random
from combat_manager.combat_manager import CombatManager

class UnitUtils:
    # Checks to see that given the player's info, a destination is able to be reached
    def valid_destination(unit, destination, game_state):
        # Gets visible and revealed tile for current player
        current_player = game_state.players.get_player(unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles
        tile = game_state.map.get_tile_hex(*destination)

        # tile doesn't exist
        if tile is None:
            return False
        
        # destination is itself
        if destination == unit.coord:
            return False
        
        # tile visible and unreachable due to terrain
        if tile.get_coords() in visibile_tiles and tile.get_movement() == -1:
            return False
        
        # tile not visible
        if tile.get_coords() not in visibile_tiles:
            return True
        
        # tile visible
        if tile.get_coords() in revealed_tiles:
            # tile occupied by unit
            if tile.unit_id is not None:
                return False
        
        return True
    
    def valid_swappable(unit, destination, game_state):
        current_player = game_state.players.get_player(unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles
        tile = game_state.map.get_tile_hex(*destination)
        if tile is None:
            return False
        
        # destination is itself
        if destination == unit.coord:
            return False
        
        # tile visible and unreachable due to terrain
        if tile.get_coords() in visibile_tiles and tile.get_movement() == -1:
            return False
        
        # tile visible
        if tile.get_coords() in revealed_tiles:
            # tile occupied by unit
            if tile.unit_id is not None:
                other_unit = game_state.units.get_unit(tile.unit_id)
                if other_unit.owner_id == unit.owner_id:
                    unit_1_path = UnitUtils.A_star(unit, destination, game_state, True)
                    unit_2_path = UnitUtils.A_star(other_unit, unit.coord, game_state, True)
                    if destination in unit_1_path:
                        unit_1_turn_reached = UnitMove.turns_to_reach(unit, destination, unit_1_path, game_state)
                        unit_2_turn_reached = UnitMove.turns_to_reach(other_unit, unit.coord, unit_2_path, game_state)
                        if unit_1_turn_reached == 1 and unit_2_turn_reached == 1:
                            return True

        
        return False
        
    
    # Given player's knowledge, is a tile in an enemy's ZOC
    def zone_of_control(unit, coord, game_state):
        if unit.follows_ZOC == False:
            return False
        current_player = game_state.players.get_player(unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles

        # Loop thru adjacent tiles
        for neighbor_direction in utils.CUBE_DIRECTIONS_DICT.keys():
            neighbor = utils.CUBE_DIRECTIONS_DICT[neighbor_direction]
            neighbor_coord = tuple(x + y for x, y in zip(coord, neighbor))
            tile = game_state.map.get_tile_hex(*neighbor_coord)

            # Adjacent tile not visible
            if tile == None or tile.get_coords() not in visibile_tiles:
                continue
            other_unit = game_state.units.get_unit(tile.unit_id)

            # No enemy unit on adjacent tile
            if other_unit == None or other_unit.owner_id == unit.owner_id:
                continue
            elif other_unit.has_ZOC == True:
                return True
        return False
    # Simple heuristic for A*
    def hex_heuristic(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2]))
    

    # A* for finding shortest path to destination given player's knowledge
    def A_star(unit, destination, game_state, swap = False, attack = False):
        current_player = game_state.players.get_player(unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles

        to_visit = []
        heapq.heappush(to_visit, (0, 0, unit.coord, None))
        visited = {}
        path = {}
        while to_visit:
            # Predicted Score, Distance to tile, Current Coord, Parent's Coord
            current_score, current_distance, current_coord, parent_coord = heapq.heappop(to_visit)

            # If tile has been reached in a more efficient manner already, then ignore and continue
            if current_coord in visited and current_distance >= visited[current_coord]:
                continue

            # Calculate movement left
            if current_coord == unit.coord:
                movement_remaining = unit.remaining_movement
            else:
                movement_remaining = (unit.movement - current_distance) % unit.movement

            # Is tile in ZOC
            enter_ZOC = UnitUtils.zone_of_control(unit, current_coord, game_state)

            path[current_coord] = parent_coord
            visited[current_coord] = current_distance

            # Destination reached
            if current_coord == destination:
                break
            current_tile = game_state.map.get_tile_hex(*current_coord)
            # Neighboring tiles
            for neighbor_direction in utils.CUBE_DIRECTIONS_DICT.keys():
                neighbor = utils.CUBE_DIRECTIONS_DICT[neighbor_direction]
                neighbor_coord = tuple(x + y for x, y in zip(current_coord, neighbor))
                tile = game_state.map.get_tile_hex(*neighbor_coord)
                # Tile doesn't exist
                if tile is None:
                    continue
                
                if swap == True and tile.get_coords() not in visibile_tiles:
                    continue

                # Tile not revealed so assume cost of 1
                if tile.get_coords() not in revealed_tiles:
                    movement_cost = 1
                else:
                    # If visible, get movement
                    movement_cost = tile.get_movement(utils.OPPOSITE_EDGES[neighbor_direction])
                    if movement_cost == -1:
                        continue
                    movement_cost = min(unit.movement, movement_cost)

                # Make sure neighbor_coord not visited yet in a more efficient manner
                if (neighbor_coord not in visited or current_distance + movement_cost < visited.get(neighbor_coord, float('inf'))):
                    
                    #Add cost if not reachable in current turn
                    if movement_remaining >= movement_cost:
                        additional_cost = 0
                    else:
                        additional_cost = unit.movement - movement_remaining
                        #If neighbor tile not reachable in current turn and previous tile already occupied, then skip tile
                        if current_tile.unit_id != None and current_coord != unit.coord:
                            continue

                    # Can't pass thru unit into tile occupied by enemy
                    if current_tile.unit_id != None and tile.unit_id != None and game_state.units.get_unit(tile.unit_id).owner_id != unit.owner_id and current_coord != unit.coord:
                        continue
                    temp_movement_remaining = movement_remaining
                    
                    #Allow unit to pass thru other units of same owner but not land on same tile
                    if tile.get_coords() in visibile_tiles:
                        if additional_cost > 0:
                            temp_movement_remaining = unit.movement
                        
                        # If neighbor tile under ZOC or currently no movement and tile occupied, don't bother going to next tile
                        if attack == False and swap == False and (temp_movement_remaining - movement_cost <= 0 or UnitUtils.zone_of_control(unit, neighbor_coord, game_state)) and tile.unit_id is not None:
                            continue

                        # Prevents pathing thru enemy units (except when attacking and it is destination)
                        if (((neighbor_coord != destination and attack == True) or attack == False) and tile.unit_id is not None and game_state.units.get_unit(tile.unit_id).owner_id != unit.owner_id):
                            continue

                    # Score to target and cost of reaching neighbor tile
                    score = current_distance + movement_cost + UnitUtils.hex_heuristic(neighbor_coord, destination) + additional_cost
                    cost = current_distance + movement_cost + additional_cost

                    # Additional turn if prev tile is ZOC
                    cost += unit.movement if enter_ZOC else 0
                    
                    heapq.heappush(to_visit, (score, cost, neighbor_coord, current_coord))

        # Convert dict to list
        full_path = []
        if destination in path:
            current = destination
            while current != unit.coord:
                full_path.append(current)
                current = path[current]
            full_path.append(unit.coord)
            full_path.reverse()
        return full_path
    
    def BFS_movement(unit, movement, game_state):
        current_player = game_state.players.get_player(unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles
        reachable = set()
        reachable_movement = {}
        queue = deque()
        queue.append((unit.coord, movement, False, False))
        while queue:
            current_coord, movement_left, unit_prior, zoc_locked = queue.popleft()
            if current_coord in reachable_movement and reachable_movement[current_coord] >= movement_left:
                continue
            
            current_tile = game_state.map.get_tile_hex(*current_coord)
            if current_tile.unit_id != None:
                other_unit = game_state.units.get_unit(current_tile.unit_id)
                if other_unit.owner_id != unit.owner_id and unit_prior:
                    continue
            reachable_movement[current_coord] = movement_left
            reachable.add(current_coord)
            enter_ZOC = UnitUtils.zone_of_control(unit, current_coord, game_state)
            is_zoc_locked = False
            if enter_ZOC and unit.coord != current_coord:
                is_zoc_locked = True
            if movement_left == 0 or zoc_locked:
                continue
            if current_tile.unit_id != None:
                other_unit = game_state.units.get_unit(current_tile.unit_id)
                if other_unit.owner_id != unit.owner_id:
                    continue
            
            
            for neighbor_direction in utils.CUBE_DIRECTIONS_DICT.keys():
                neighbor = utils.CUBE_DIRECTIONS_DICT[neighbor_direction]
                neighbor_coord = tuple(x + y for x, y in zip(current_coord, neighbor))
                tile = game_state.map.get_tile_hex(*neighbor_coord)
                if tile is None:
                    continue
                if tile.get_coords() not in revealed_tiles:
                    continue
                else:
                    movement_cost = tile.get_movement(utils.OPPOSITE_EDGES[neighbor_direction])
                    if movement_cost == -1:
                        continue
                    movement_cost = min(unit.movement, movement_cost)
                if movement_left - movement_cost >= 0:
                    queue.append((tile.get_coords(), movement_left - movement_cost, True if (current_tile.unit_id != None and current_tile.get_coords() != unit.coord) else False, is_zoc_locked))
        return reachable
    
class UnitMove:

    # Next tile in pre-calculated path is available. Important when unit has more movement than visibility and path goes thru impassable terrain or opposing units
    def valid_tile_move(unit, next_tile, game_state):

        # Impassable Terrain (Mountain)
        if next_tile.get_movement() == -1:
            return False
        
        # Enemy unit occupies tile
        if next_tile.unit_id != None:
            next_tile_unit = game_state.units.get_unit(next_tile.unit_id)
            if next_tile_unit.owner_id != unit.owner_id:
                return False
        return True
    
    def turns_to_reach(unit, destination, full_path, game_state):
        current_player = game_state.players.get_player(unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles
        movement_left = unit.remaining_movement
        turn_reached = 0
        for x in range(len(full_path)):
            tile = game_state.map.get_tile_hex(*full_path[x])
            enter_ZOC = UnitUtils.zone_of_control(unit, tile.get_coords(), game_state)
            if enter_ZOC and tile.get_coords() != unit.coord:
                movement_left = 0
            if tile.get_coords() == destination:
                return turn_reached + 1
            
            next_tile = game_state.map.get_tile_hex(*full_path[x + 1])
            direction = utils.get_relative_position(tile.get_coords(), next_tile.get_coords())
            direction = utils.OPPOSITE_EDGES[direction]
            if next_tile.get_coords() in revealed_tiles:
                next_tile_movement = min(unit.movement, next_tile.get_movement(direction))
            else:
                next_tile_movement = 1
            if movement_left - next_tile_movement < 0:
                turn_reached += 1
                movement_left = unit.movement - next_tile_movement
            else:
                movement_left -= next_tile_movement
        return -1
    
    def move_to(unit, destination, game_state):
        #Given the player's current knowledge, is the destination reachable?
        if not UnitUtils.valid_destination(unit, destination, game_state):
            unit.destination = None
            unit.path = None
            return True
        unit.fortified = False
        unit.turns_fortified = 0
        unit.fortify_and_heal = False
        unit.destination = destination
        full_path = UnitUtils.A_star(unit, destination, game_state)

        #Account for tile visibility
        current_player = game_state.players.get_player(unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles

        #Find next tile for unit to move to
        if destination in full_path:
            unit.path = full_path
            movement_left = unit.remaining_movement
            if unit.ZOC_locked:
                movement_left = 0
            turn_reached = 0
            orig_tile = game_state.map.get_tile_hex(*unit.coord)
            for x in range(len(full_path)):
                tile = game_state.map.get_tile_hex(*full_path[x])
                enter_ZOC = UnitUtils.zone_of_control(unit, tile.get_coords(), game_state)
                if enter_ZOC and tile.get_coords() != unit.coord:
                    unit.ZOC_locked = True
                    orig_tile.unit_id = None
                    tile.unit_id = unit.id
                    unit.coord = tile.get_coords()
                    break
                unit.coord = tile.get_coords()
                current_player.update_visibility()
                
                if (tile.x, tile.y, tile.z) == destination:
                    orig_tile.unit_id = None
                    tile.unit_id = unit.id
                    unit.coord = tile.get_coords()
                    break
                
                # Update visibility of unit at tile
                next_tile = game_state.map.get_tile_hex(*full_path[x + 1])
                # See if next tile is reachable. If not, then move unit to tile and redo A*.
                if UnitMove.valid_tile_move(unit, next_tile, game_state) == False:
                    orig_tile.unit_id = None
                    tile.unit_id = unit.id
                    unit.remaining_movement = movement_left


                    return False


                direction = utils.get_relative_position(tile.get_coords(), next_tile.get_coords())
                direction = utils.OPPOSITE_EDGES[direction]

                
                next_tile_movement = min(unit.movement, next_tile.get_movement(direction))
                

                
                if movement_left - next_tile_movement < 0:
                    orig_tile.unit_id = None
                    tile.unit_id = unit.id
                    unit.coord = tile.get_coords()
                    break
                else:
                    movement_left -= next_tile_movement
            unit.remaining_movement = movement_left
        if unit.coord == unit.destination:
            unit.destination = None
            unit.path = None
        return True

    def swap_units(unit, destination, destination_unit, game_state):
        unit_1_path = UnitUtils.A_star(unit, destination, game_state, True)
        unit_2_path = UnitUtils.A_star(destination_unit, unit.coord, game_state, True)
        if destination in unit_1_path:
            unit_1_turn_reached = UnitMove.turns_to_reach(unit, destination, unit_1_path, game_state)
            unit_2_turn_reached = UnitMove.turns_to_reach(destination_unit, unit.coord, unit_2_path, game_state)
            if unit_1_turn_reached == 1 and unit_2_turn_reached == 1:
                UnitMove.swap_move(destination_unit, unit.coord, unit_2_path, game_state)
                UnitMove.swap_move(unit, destination, unit_1_path, game_state)

            
    def swap_move(unit, destination, full_path, game_state):
        current_player = game_state.players.get_player(unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles
        movement_left = unit.remaining_movement
        turn_reached = 0
        orig_tile = game_state.map.get_tile_hex(*unit.coord)
        for x in range(len(full_path)):
            tile = game_state.map.get_tile_hex(*full_path[x])
            enter_ZOC = UnitUtils.zone_of_control(unit, tile.get_coords(), game_state)
            if enter_ZOC and tile.get_coords() != unit.coord:
                movement_left = 0
            unit.coord = tile.get_coords()
            current_player.update_visibility()
            
            if tile.get_coords() == destination:
                tile.unit_id = unit.id
                unit.coord = tile.get_coords()
                break
            
            # Update visibility of unit at tile
            next_tile = game_state.map.get_tile_hex(*full_path[x + 1])
            # See if next tile is reachable. If not, then move unit to tile and redo A*.

            direction = utils.get_relative_position(tile.get_coords(), next_tile.get_coords())
            direction = utils.OPPOSITE_EDGES[direction]

            
            next_tile_movement = min(unit.movement, next_tile.get_movement(direction))
            
            
            movement_left -= next_tile_movement
        unit.remaining_movement = movement_left
        unit.fortified = False
        unit.turns_fortified = 0
        unit.fortify_and_heal = False


    def swap_hover(unit, destination, destination_unit, game_state):
        unit_1_path = UnitUtils.A_star(unit, destination, game_state, True)
        unit_2_path = UnitUtils.A_star(destination_unit, unit.coord, game_state, True)
        if destination in unit_1_path:
            unit_1_turn_reached = UnitMove.turns_to_reach(unit, destination, unit_1_path, game_state)
            unit_2_turn_reached = UnitMove.turns_to_reach(destination_unit, unit.coord, unit_2_path, game_state)
            if unit_1_turn_reached == 1 and unit_2_turn_reached == 1:
                UnitMove.display_hover_path(unit, unit_1_path, destination, game_state)


    def clear_hover_path(unit, game_state):
        if unit.hover_destination is not None:
            if unit.hover_path != None and len(unit.hover_path) > 0:
                for coord in unit.hover_path:
                    tile = game_state.map.get_tile_hex(*coord)
                    if tile is not None:
                        tile.path = False
                        tile.neighbor = None
                        tile.turn_reached = -1
            unit.hover_destination = None
            unit.hover_path = None
        
    def display_hover_path(unit, full_path, destination, game_state):
        current_player = game_state.players.get_player(unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles
        movement_left = unit.remaining_movement
        if unit.ZOC_locked:
            movement_left = 0
        turn_reached = 0
        for x in range(len(full_path)):
            tile = game_state.map.get_tile_hex(*full_path[x])
            enter_ZOC = UnitUtils.zone_of_control(unit, tile.get_coords(), game_state)
            if enter_ZOC and tile.get_coords() != unit.coord:
                movement_left = 0
            if (tile.x, tile.y, tile.z) == destination:
                tile.path = True
                tile.turn_reached = turn_reached + 1
                break
            elif (tile.x, tile.y, tile.z) == unit.coord:
                tile.neighbor = game_state.map.get_tile_hex(*full_path[x + 1])
                tile.path = True
            else:
                tile.neighbor = game_state.map.get_tile_hex(*full_path[x + 1])
                tile.path = True
            
            next_tile = game_state.map.get_tile_hex(*full_path[x + 1])
            direction = utils.get_relative_position(tile.get_coords(), next_tile.get_coords())
            direction = utils.OPPOSITE_EDGES[direction]
            if next_tile.get_coords() in revealed_tiles:
                next_tile_movement = min(unit.movement, next_tile.get_movement(direction))
            else:
                next_tile_movement = 1
            if movement_left - next_tile_movement < 0:
                tile.turn_reached = turn_reached + 1
                turn_reached += 1
                movement_left = unit.movement - next_tile_movement
            else:
                movement_left -= next_tile_movement
        unit.hover_path = full_path

    def BFS_movement(unit, game_state):
        current_player = game_state.players.get_player(unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles
        reachable = set()
        reachable_movement = {}
        queue = deque()
        queue.append((unit.coord, unit.remaining_movement, False, False))
        while queue:
            current_coord, movement_left, unit_prior, zoc_locked = queue.popleft()
            if current_coord in reachable_movement and reachable_movement[current_coord] >= movement_left:
                continue
            
            current_tile = game_state.map.get_tile_hex(*current_coord)
            if current_tile.unit_id != None:
                other_unit = game_state.units.get_unit(current_tile.unit_id)
                if other_unit.owner_id != unit.owner_id and unit_prior:
                    continue
            reachable_movement[current_coord] = movement_left
            reachable.add(current_coord)
            enter_ZOC = UnitUtils.zone_of_control(unit, current_coord, game_state)
            is_zoc_locked = False
            if enter_ZOC and unit.coord != current_coord:
                is_zoc_locked = True
            if movement_left == 0 or zoc_locked:
                continue
            if current_tile.unit_id != None:
                other_unit = game_state.units.get_unit(current_tile.unit_id)
                if other_unit.owner_id != unit.owner_id:
                    continue
            
            
            for neighbor_direction in utils.CUBE_DIRECTIONS_DICT.keys():
                neighbor = utils.CUBE_DIRECTIONS_DICT[neighbor_direction]
                neighbor_coord = tuple(x + y for x, y in zip(current_coord, neighbor))
                tile = game_state.map.get_tile_hex(*neighbor_coord)
                if tile is None:
                    continue
                if tile.get_coords() not in revealed_tiles:
                    continue
                else:
                    movement_cost = tile.get_movement(utils.OPPOSITE_EDGES[neighbor_direction])
                    if movement_cost == -1:
                        continue
                    movement_cost = min(unit.movement, movement_cost)
                if movement_left - movement_cost >= 0:
                    queue.append((tile.get_coords(), movement_left - movement_cost, True if (current_tile.unit_id != None and current_tile.get_coords() != unit.coord) else False, is_zoc_locked))
        return reachable

class UnitVisibility:
    def BFS_visibility(unit, visibility, game_state): 
        tile = game_state.map.get_tile_hex(*unit.coord)
        
        visibile = set()
        visited_visibility = {}
        queue = deque()
        queue.append((unit.coord, visibility, unit.vision))
        while queue:
            current_coord, visibility, distance = queue.popleft()
            if current_coord in visited_visibility and visited_visibility[current_coord] >= visibility:
                continue
            visited_visibility[current_coord] = visibility
            
            # Did it this way so mountains are visible
            if distance - 1 < -1:
                continue
            
            
            for neighbor_direction in utils.CUBE_DIRECTIONS_DICT.keys():
                neighbor = utils.CUBE_DIRECTIONS_DICT[neighbor_direction]
                neighbor_coord = tuple(x + y for x, y in zip(current_coord, neighbor))
                tile = game_state.map.get_tile_hex(*neighbor_coord)     
                if tile is not None and tile.get_coords():  
                    neighbor_visibility_bonus = tile_config.biomes[tile.biome]["Terrain"][tile.terrain]["visibility_bonus"]
                    neighbor_visibility_penalty = tile_config.biomes[tile.biome]["Terrain"][tile.terrain]["visibility_penalty"]

                    if tile.feature != None:
                        neighbor_visibility_bonus += tile_config.biomes[tile.biome]["Feature"][tile.feature]["visibility_bonus"]
                        neighbor_visibility_penalty += tile_config.biomes[tile.biome]["Feature"][tile.feature]["visibility_penalty"]

                    if visibility > 0 and visibility + neighbor_visibility_bonus > 0 and distance > 0:
                        visibile.add(neighbor_coord) 
                    
                    elif visibility + neighbor_visibility_bonus > 0 and tile.terrain == "Mountain":
                        visibile.add(neighbor_coord) 
                    
                    queue.append((tile.get_coords(), visibility - neighbor_visibility_penalty, distance - 1))
        return visibile   
    
class UnitAttack:
    def BFS_ranged_attack(unit, game_state):
        tile = game_state.map.get_tile_hex(*unit.coord)

        
        visibile = set()
        visited_visibility = {}
        queue = deque()
        queue.append((unit.coord, unit.range, unit.vision))
        while queue:
            current_coord, visibility, distance = queue.popleft()
            if current_coord in visited_visibility and visited_visibility[current_coord] >= visibility:
                continue
            visited_visibility[current_coord] = visibility
            
            # Did it this way so mountains are visible
            if distance - 1 < 0:
                continue
            
            
            for neighbor_direction in utils.CUBE_DIRECTIONS_DICT.keys():
                neighbor = utils.CUBE_DIRECTIONS_DICT[neighbor_direction]
                neighbor_coord = tuple(x + y for x, y in zip(current_coord, neighbor))
                tile = game_state.map.get_tile_hex(*neighbor_coord)     
                if tile is not None and tile.get_coords():  
                    neighbor_visibility_bonus = tile_config.biomes[tile.biome]["Terrain"][tile.terrain]["visibility_bonus"]
                    neighbor_visibility_penalty = tile_config.biomes[tile.biome]["Terrain"][tile.terrain]["visibility_penalty"]

                    if tile.feature != None:
                        neighbor_visibility_bonus += tile_config.biomes[tile.biome]["Feature"][tile.feature]["visibility_bonus"]
                        neighbor_visibility_penalty += tile_config.biomes[tile.biome]["Feature"][tile.feature]["visibility_penalty"]

                    if visibility > 0 and visibility + neighbor_visibility_bonus > 0 and distance > 0:
                        visibile.add(neighbor_coord) 
                    
                    elif visibility + neighbor_visibility_bonus > 0 and tile.terrain == "Mountain":
                        visibile.add(neighbor_coord) 
                    
                    queue.append((tile.get_coords(), visibility - neighbor_visibility_penalty, distance - 1))
        return visibile 
    
    def ranged_attack(unit, destination, game_state, visual_effects):
        attackable_tiles = UnitAttack.get_attackable_units(unit, game_state)
        if destination not in attackable_tiles or unit.remaining_movement == 0:
            return unit.movement
        enemy_tile = game_state.map.get_tile_hex(*destination)
        current_tile = game_state.map.get_tile_hex(*unit.coord)
        enemy_unit = game_state.units.get_unit(enemy_tile.unit_id)
        damage_inflicted, damage_taken = CombatManager.combat(unit, enemy_unit, current_tile, enemy_tile, "ranged")
        enemy_unit.health -= damage_inflicted
        if enemy_unit.health <= 0:
            enemy_unit.killed()
            enemy_tile.unit_id = None

        
        unit.remaining_movement = 0
        visual_effects.add_damage(damage_inflicted, enemy_tile.get_coords(), True)
        UnitAttack.clear_attackable(unit, game_state)
        UnitMove.clear_hover_path(unit, game_state)

    def melee_attack(unit, destination, game_state, visual_effects):
        attackable_tiles = UnitAttack.get_attackable_units(unit, game_state)
        if destination not in attackable_tiles or unit.remaining_movement == 0:
            return unit.movement
        full_path = UnitUtils.A_star(unit, destination, game_state, False, True)
        current_player = game_state.players.get_player(unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles

        #Find next tile for unit to move to
        if destination in full_path:
            unit.path = full_path
            movement_left = unit.remaining_movement
            turn_reached = 0
            orig_tile = game_state.map.get_tile_hex(*unit.coord)
            for x in range(len(full_path)):
                tile = game_state.map.get_tile_hex(*full_path[x])
                enter_ZOC = UnitUtils.zone_of_control(unit, tile.get_coords(), game_state)
                if enter_ZOC and tile.get_coords() != unit.coord:
                    unit.ZOC_locked = True
                    orig_tile.unit_id = None
                    tile.unit_id = unit.id
                    unit.coord = tile.get_coords()
                    break
                unit.coord = tile.get_coords()
                current_player.update_visibility()
                
                
                # Update visibility of unit at tile
                next_tile = game_state.map.get_tile_hex(*full_path[x + 1])
                
                if next_tile.get_coords() == destination:
                    orig_tile.unit_id = None
                    tile.unit_id = unit.id
                    unit.coord = tile.get_coords()
                    break


                direction = utils.get_relative_position(tile.get_coords(), next_tile.get_coords())
                direction = utils.OPPOSITE_EDGES[direction]

                
                next_tile_movement = min(unit.movement, next_tile.get_movement(direction))
                

                
                if movement_left - next_tile_movement < 0:
                    orig_tile.unit_id = None
                    tile.unit_id = unit.id
                    unit.coord = tile.get_coords()
                    break
                else:
                    movement_left -= next_tile_movement
            unit.remaining_movement = movement_left
        enemy_tile = game_state.map.get_tile_hex(*destination)
        current_tile = game_state.map.get_tile_hex(*unit.coord)
        enemy_unit = game_state.units.get_unit(enemy_tile.unit_id)
        damage_inflicted, damage_taken = CombatManager.combat(unit, enemy_unit, current_tile, enemy_tile, "melee")
        visual_effects.add_damage(damage_inflicted, enemy_tile.get_coords(), True)
        visual_effects.add_damage(damage_taken, current_tile.get_coords(), False)

        unit.health -= damage_taken
        enemy_unit.health -= damage_inflicted
        if enemy_unit.health <= 0:
            enemy_unit.killed()
            enemy_tile.unit_id = unit.id
            current_tile.unit_id = None
            unit.coord = enemy_tile.get_coords()
            current_tile = game_state.map.get_tile_hex(*unit.coord)

        if unit.health <= 0:
            unit.killed()
            current_tile.unit_id = None
        
        unit.remaining_movement = 0
            
        UnitAttack.clear_attackable(unit, game_state)
        UnitMove.clear_hover_path(unit, game_state)

    def get_attackable_units(unit, game_state):
        current_player = game_state.players.get_player(unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles
        tiles_in_range = UnitMove.BFS_movement(unit, game_state) if unit.type != "Ranged" else UnitAttack.BFS_ranged_attack(unit, game_state)
        tiles_in_range &= visibile_tiles

        attackable_tiles = set()
        for tile_coord in tiles_in_range:
            tile = game_state.map.get_tile_hex(*tile_coord)     
            if tile.unit_id != None:
                other_unit = game_state.units.get_unit(tile.unit_id)
                if other_unit.owner_id != unit.owner_id:
                    attackable_tiles.add(tile_coord)
        return attackable_tiles
    
    def highlight_attackable(unit, game_state):
        attackable_tiles = UnitAttack.get_attackable_units(unit, game_state)
        unit.attackable_tiles = attackable_tiles
        for tile_coord in attackable_tiles:
            tile = game_state.map.get_tile_hex(*tile_coord)     
            tile.attackable = True
            
    def clear_attackable(unit, game_state):
        for tile_coord in unit.attackable_tiles:
            tile = game_state.map.get_tile_hex(*tile_coord)     
            tile.attackable = False

class UnitScoringUtils:
    def BFS_movement(unit, tile_coord, movement, game_state):
        current_player = game_state.players.get_player(unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles
        reachable = set()
        reachable_movement = {}
        queue = deque()
        queue.append((tile_coord, movement, False, False))
        while queue:
            current_coord, movement_left, unit_prior, zoc_locked = queue.popleft()
            if current_coord in reachable_movement and reachable_movement[current_coord] >= movement_left:
                continue
            
            current_tile = game_state.map.get_tile_hex(*current_coord)
            if current_tile.unit_id != None:
                other_unit = game_state.units.get_unit(current_tile.unit_id)
                if other_unit.owner_id != unit.owner_id and unit_prior:
                    continue
            reachable_movement[current_coord] = movement_left
            reachable.add(current_coord)
            enter_ZOC = UnitUtils.zone_of_control(unit, current_coord, game_state)
            is_zoc_locked = False
            if enter_ZOC and unit.coord != current_coord:
                is_zoc_locked = True
            if movement_left == 0 or zoc_locked:
                continue
            if current_tile.unit_id != None:
                other_unit = game_state.units.get_unit(current_tile.unit_id)
                if other_unit.owner_id != unit.owner_id:
                    continue
            
            
            for neighbor_direction in utils.CUBE_DIRECTIONS_DICT.keys():
                neighbor = utils.CUBE_DIRECTIONS_DICT[neighbor_direction]
                neighbor_coord = tuple(x + y for x, y in zip(current_coord, neighbor))
                tile = game_state.map.get_tile_hex(*neighbor_coord)
                if tile is None:
                    continue
                if tile.get_coords() not in revealed_tiles:
                    continue
                else:
                    movement_cost = tile.get_movement(utils.OPPOSITE_EDGES[neighbor_direction])
                    if movement_cost == -1:
                        continue
                    movement_cost = min(unit.movement, movement_cost)
                if movement_left - movement_cost >= 0:
                    queue.append((tile.get_coords(), movement_left - movement_cost, True if (current_tile.unit_id != None and current_tile.get_coords() != unit.coord) else False, is_zoc_locked))
        return reachable
    
    def BFS_nearby_units(unit, tile_coord, movement, game_state):
        current_player = game_state.players.get_player(unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles
        reachable = set()
        reachable_movement = {}
        queue = deque()
        queue.append((tile_coord, movement))
        while queue:
            current_coord, movement_left = queue.popleft()
            if current_coord in reachable_movement and reachable_movement[current_coord] >= movement_left:
                continue
            
            current_tile = game_state.map.get_tile_hex(*current_coord)
            if current_tile.unit_id != None:
                other_unit = game_state.units.get_unit(current_tile.unit_id)
            reachable_movement[current_coord] = movement_left
            reachable.add(current_coord)
            enter_ZOC = UnitUtils.zone_of_control(unit, current_coord, game_state)
            if movement_left == 0:
                continue
            if current_tile.unit_id != None:
                other_unit = game_state.units.get_unit(current_tile.unit_id)
                if other_unit.owner_id != unit.owner_id:
                    continue
            
            
            for neighbor_direction in utils.CUBE_DIRECTIONS_DICT.keys():
                neighbor = utils.CUBE_DIRECTIONS_DICT[neighbor_direction]
                neighbor_coord = tuple(x + y for x, y in zip(current_coord, neighbor))
                tile = game_state.map.get_tile_hex(*neighbor_coord)
                if tile is None:
                    continue
                if tile.get_coords() not in visibile_tiles:
                    continue
                else:
                    movement_cost = tile.get_movement(utils.OPPOSITE_EDGES[neighbor_direction])
                    if movement_cost == -1:
                        continue
                    movement_cost = min(unit.movement, movement_cost)
                if movement_left - movement_cost >= 0:
                    queue.append((tile.get_coords(), movement_left - movement_cost))
        return reachable
    
    def BFS_ranged_attack(unit, tile_coord, game_state):
        tile = game_state.map.get_tile_hex(*unit.coord)

        
        visibile = set()
        visited_visibility = {}
        queue = deque()
        queue.append((tile_coord, unit.range, unit.vision))
        while queue:
            current_coord, visibility, distance = queue.popleft()
            if current_coord in visited_visibility and visited_visibility[current_coord] >= visibility:
                continue
            visited_visibility[current_coord] = visibility
            
            # Did it this way so mountains are visible
            if distance - 1 < 0:
                continue
            
            
            for neighbor_direction in utils.CUBE_DIRECTIONS_DICT.keys():
                neighbor = utils.CUBE_DIRECTIONS_DICT[neighbor_direction]
                neighbor_coord = tuple(x + y for x, y in zip(current_coord, neighbor))
                tile = game_state.map.get_tile_hex(*neighbor_coord)     
                if tile is not None and tile.get_coords():  
                    neighbor_visibility_bonus = tile_config.biomes[tile.biome]["Terrain"][tile.terrain]["visibility_bonus"]
                    neighbor_visibility_penalty = tile_config.biomes[tile.biome]["Terrain"][tile.terrain]["visibility_penalty"]

                    if tile.feature != None:
                        neighbor_visibility_bonus += tile_config.biomes[tile.biome]["Feature"][tile.feature]["visibility_bonus"]
                        neighbor_visibility_penalty += tile_config.biomes[tile.biome]["Feature"][tile.feature]["visibility_penalty"]

                    if visibility > 0 and visibility + neighbor_visibility_bonus > 0 and distance > 0:
                        visibile.add(neighbor_coord) 
                    
                    elif visibility + neighbor_visibility_bonus > 0 and tile.terrain == "Mountain":
                        visibile.add(neighbor_coord) 
                    
                    queue.append((tile.get_coords(), visibility - neighbor_visibility_penalty, distance - 1))
        return visibile 
    
    def djikstra(unit, tile_coord, game_state):
        current_player = game_state.players.get_player(unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles
        tile_score = {}
        visited_tiles = set()
        path = {}
        heap = [(0, tile_coord)]
        tile_score[tile_coord] = 0
        visibile_tiles.add(tile_coord)
        
        while heap:
            current_distance, current_tile_coord = heapq.heappop(heap)
            if current_tile_coord in visited_tiles:
                continue
            visited_tiles.add(current_tile_coord)
            # Is tile in ZOC
            if current_tile_coord == tile_coord:
                movement_remaining = unit.remaining_movement
            else:
                movement_remaining = (unit.movement - current_distance) % unit.movement
            enter_ZOC = UnitUtils.zone_of_control(unit, current_tile_coord, game_state)
            current_tile = game_state.map.get_tile_hex(*current_tile_coord)
            for neighbor_direction in utils.CUBE_DIRECTIONS_DICT.keys():
                neighbor = utils.CUBE_DIRECTIONS_DICT[neighbor_direction]
                neighbor_coord = tuple(x + y for x, y in zip(current_tile_coord, neighbor))
                tile = game_state.map.get_tile_hex(*neighbor_coord)
                # Tile doesn't exist
                if tile is None:
                    continue

                # Tile not revealed so assume cost of 1
                if tile.get_coords() not in revealed_tiles:
                    movement_cost = 1
                else:
                    # If visible, get movement
                    movement_cost = tile.get_movement(utils.OPPOSITE_EDGES[neighbor_direction])
                    if movement_cost == -1:
                        continue
                    movement_cost = min(unit.movement, movement_cost)

                # Make sure neighbor_coord not visited yet in a more efficient manner
               
                    
                #Add cost if not reachable in current turn
                if movement_remaining >= movement_cost:
                    additional_cost = 0
                else:
                    additional_cost = unit.movement - movement_remaining
                    if current_tile.unit_id != None:
                        continue
                temp_movement_remaining = movement_remaining

                # Can't pass thru unit into tile occupied by enemy
                if current_tile.unit_id != None and tile.unit_id != None and game_state.units.get_unit(tile.unit_id).owner_id != unit.owner_id:
                    continue
                
                #Allow unit to pass thru other units of same owner but not land on same tile
                if tile.get_coords() in visibile_tiles:
                    if additional_cost > 0:
                        temp_movement_remaining = unit.movement
                    if (temp_movement_remaining - movement_cost <= 0 or UnitUtils.zone_of_control(unit, neighbor_coord, game_state)) and tile.unit_id is not None:
                        continue
                    if tile.unit_id is not None and game_state.units.get_unit(tile.unit_id).owner_id != unit.owner_id:
                        continue

                # Score to target and cost of reaching neighbor tile
                cost = current_distance + movement_cost + additional_cost

                # Additional turn if prev tile is ZOC
                cost += unit.movement if enter_ZOC else 0

                if tile_score.get(neighbor_coord, None) == None or tile_score.get(neighbor_coord, None) > cost:
                    tile_score[neighbor_coord] = cost
                    path[neighbor_coord] = current_tile_coord
                
                heapq.heappush(heap, (cost, neighbor_coord))
        return path
class UnitMoveScoring:
    def legal_destination(unit, destination, game_state):

        # Gets visible and revealed tile for current player
        current_player = game_state.players.get_player(unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles
        tile = game_state.map.get_tile_hex(*destination)

        # tile doesn't exist
        if tile is None:
            return False
        
        # destination is itself
        if destination == unit.coord:
            return False
        
        # tile visible and unreachable due to terrain
        if tile.get_coords() in visibile_tiles and tile.get_movement() == -1:
            return False
        
        # tile visible
        if tile.get_coords() in visibile_tiles:
            # tile occupied by unit
            if tile.unit_id is not None:
                return False
        #path = UnitUtils.A_star(unit, destination, game_state)
        #if destination not in path:
        #    return False
        
        return True

    def get_attackable_units(unit, tile_coord, game_state):
        current_player = game_state.players.get_player(unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles
        tiles_in_range = UnitScoringUtils.BFS_movement(unit, tile_coord, unit.movement, game_state) if unit.type != "Ranged" else UnitScoringUtils.BFS_ranged_attack(unit, tile_coord, game_state)
        tiles_in_range &= visibile_tiles

        attackable_tiles = set()
        for tile_coord in tiles_in_range:
            tile = game_state.map.get_tile_hex(*tile_coord)     
            if tile.unit_id != None:
                other_unit = game_state.units.get_unit(tile.unit_id)
                if other_unit.owner_id != unit.owner_id:
                    attackable_tiles.add(tile_coord)
        return attackable_tiles
    
    def get_attackable_tiles(unit, tile_coord, game_state):
        current_player = game_state.players.get_player(unit.owner_id)
        revealed_tiles = current_player.revealed_tiles
        visibile_tiles = current_player.visible_tiles
        tiles_in_range = UnitScoringUtils.BFS_movement(unit, tile_coord, unit.movement, game_state) if unit.type != "Ranged" else UnitScoringUtils.BFS_ranged_attack(unit, tile_coord, game_state)
        tiles_in_range &= visibile_tiles

        return tiles_in_range