import config as config
import utils as utils
import generator.unit_generator_config as unit_generator_config
import generator.map_generator_config as map_generator_config

import random
from sklearn.cluster import KMeans
from collections import deque
import heapq



class UnitGenerator:
    def __init__(self, game_state):
        seed = random.randint(0, 2**32 - 1)
        self.rng = random.Random(seed) if seed != '' else random.Random()
        self.game_state = game_state
        self.ROWS, self.COLUMNS = config.map_settings["tile_height"], config.map_settings["tile_width"]
        self.player_tiles = {}
        self.tile_scores = {}

    def generate_units(self):
        self.game_state.units.remove_all_units()
        self.choose_spawn_locations()
        for key in self.player_tiles.keys():
            num_units = unit_generator_config.PlayerUnits[key]["Melee"] + unit_generator_config.PlayerUnits[key]["Ranged"] + unit_generator_config.PlayerUnits[key]["Cavalry"]
            cluster = self.player_tiles[key]
            spawn_tile = cluster[0][0]
            tiles = self.BFS_spawn(spawn_tile, num_units, key)
            units = ["Melee"] * unit_generator_config.PlayerUnits[key]["Melee"] + ["Ranged"] * unit_generator_config.PlayerUnits[key]["Ranged"] + ["Cavalry"] * unit_generator_config.PlayerUnits[key]["Cavalry"]
            self.rng.shuffle(units)
            for i, tile in enumerate(tiles):
                self.game_state.players.get_player(key).place_unit(units[i], *tile)



            


    def choose_spawn_locations(self):
        traversable_tiles = []
        num_players = config.num_players
        tiles = self.game_state.map.tiles
        for tile_coord in tiles.keys():
            tile = tiles[tile_coord]
            if tile.movement != -1:
                euclidean_coord = utils.hex_coord_to_coord(*tile_coord)
                traversable_tiles.append(euclidean_coord)
        kmeans = KMeans(n_clusters=num_players)
        clusters = kmeans.fit_predict(traversable_tiles)
        cluster_centers = kmeans.cluster_centers_
        rounded_centers = []
        """ for center in cluster_centers:
            x = max(min(round(center[0]), self.COLUMNS - 1), 0)
            y = max(min(round(center[1]), self.ROWS - 1), 0)
            hex_coord = utils.coord_to_hex_coord(y, x)
            rounded_centers.append(hex_coord) """
        player_tiles = {}
        for i, tile in enumerate(traversable_tiles):
            hex_coord = utils.coord_to_hex_coord(tile[1], tile[0])
            player_tiles.setdefault(clusters[i], []).append([hex_coord])

        for cluster in player_tiles.keys():
            for player_index in range(len(player_tiles[cluster])):
                tile = player_tiles[cluster][player_index][0]
                distance_to_enemy_tile = float('inf')
                for enemy_cluster in player_tiles.keys():
                    if cluster == enemy_cluster:
                        continue
                    for enemy_index in range(len(player_tiles[enemy_cluster])):
                        enemy_tile = player_tiles[enemy_cluster][enemy_index][0]
                        distance_to_enemy_tile = min(distance_to_enemy_tile, self.hex_heuristic(tile, enemy_tile))
                spawnable_tiles = self.BFS_area(tile, 2)
                score = len(spawnable_tiles) * (distance_to_enemy_tile / (distance_to_enemy_tile + 1))
                player_tiles[cluster][player_index] = [tile, score]
                self.tile_scores[tile] = score
        for cluster in player_tiles.keys():
            player_tiles[cluster].sort(reverse = True, key = lambda x: x[1])
        self.player_tiles = player_tiles




    def hex_heuristic(self, a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2]))
    
    def BFS_area(self, tile_coord, range):
        reachable = set()
        queue = deque()
        queue.append((tile_coord, range))
        while queue:
            current_coord, range = queue.popleft()
            if current_coord in reachable or range < 0:
                continue
            reachable.add(current_coord)
            
            
            
            for neighbor_direction in utils.CUBE_DIRECTIONS_DICT.keys():
                neighbor = utils.CUBE_DIRECTIONS_DICT[neighbor_direction]
                neighbor_coord = tuple(x + y for x, y in zip(current_coord, neighbor))
                if self.game_state.map.get_tile_hex(*neighbor_coord) is None or self.game_state.map.get_tile_hex(*neighbor_coord).movement == -1:
                    continue
                
                queue.append((neighbor_coord, range - 1))
        return reachable

    def BFS_spawn(self, tile_coord, num_units, player):
        #prioritize tiles by score.
        to_visit = []
        visited = []
        spawnable_tiles = []
        heapq.heappush(to_visit, (0, tile_coord))
        
        while to_visit and len(spawnable_tiles) < num_units:
            # Predicted Score, Distance to tile, Current Coord, Parent's Coord
            current_score, current_coord = heapq.heappop(to_visit)

            # If tile has been reached in a more efficient manner already, then ignore and continue
            if current_coord in visited:
                continue
            
            visited.append(current_coord)
            if [current_coord, -current_score] in self.player_tiles[player]:
                spawnable_tiles.append(current_coord)
                if len(spawnable_tiles) >= num_units:
                    break
            
            # Neighboring tiles
            for neighbor_direction in utils.CUBE_DIRECTIONS_DICT.keys():
                neighbor = utils.CUBE_DIRECTIONS_DICT[neighbor_direction]
                neighbor_coord = tuple(x + y for x, y in zip(current_coord, neighbor))
                tile = self.game_state.map.get_tile_hex(*neighbor_coord)
                # Tile doesn't exist
                if tile is None or tile.movement == -1:
                    continue
                
                
                heapq.heappush(to_visit, (-self.tile_scores[neighbor_coord], neighbor_coord))

        return spawnable_tiles

    #def score_tile(self):
