import config as config
import utils as utils
from sklearn.cluster import KMeans
from collections import deque



class UnitGenerator:
    def __init__(self, game_state):
        self.game_state = game_state
        self.ROWS, self.COLUMNS = config.map_settings["tile_height"], config.map_settings["tile_width"]


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

    def spawn_units(self):
        pass


    #def score_tile(self):
