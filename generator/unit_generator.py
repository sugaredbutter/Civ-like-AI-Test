import config as config
import utils as utils
from sklearn.cluster import KMeans



class UnitGenerator:
    def __init__(self, game_state):
        self.game_state = game_state

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
        kmeans.fit(traversable_tiles)
        cluster_centers = kmeans.cluster_centers_
        print(cluster_centers)