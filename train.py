import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import Adam

import utils as utils
import config as config
from machine_learning.environment_setup import MLEnv
from Agents.actions import Actions
from Agents.actions import CompleteUnitAction
from combat_manager.combat_manager import CombatManager
from units.units_utils import UnitUtils


ROWS, COLUMNS = config.map_settings["tile_height"], config.map_settings["tile_width"]


# Reference
class GameTransformer(nn.Module):
    def __init__(self, tile_dim, action_dim, embed_dim=128, nhead=4, num_layers=2):
        super().__init__()
        self.tile_embed = nn.Linear(tile_dim, embed_dim)
        self.action_embed = nn.Linear(action_dim, embed_dim)

        encoder_layer = nn.TransformerEncoderLayer(d_model=embed_dim, nhead=nhead)
        self.map_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        cross_layer = nn.TransformerEncoderLayer(d_model=embed_dim, nhead=nhead)
        self.action_encoder = nn.TransformerEncoder(cross_layer, num_layers=num_layers)
        
        self.action_head = nn.Linear(embed_dim, 1)   # score for each action
        self.value_head = nn.Linear(embed_dim, 1)    # value estimate for the map

    def forward(self, map_feats, action_feats):
        """
        map_feats: (num_tiles, tile_dim)
        action_feats: (num_actions, action_dim)
        """
        # Embed and add positional encodings
        map_emb = self.tile_embed(map_feats)  # (num_tiles, embed_dim)
        action_emb = self.action_embed(action_feats)  # (num_actions, embed_dim)

        # Encode map (context)
        map_context = self.map_encoder(map_emb.unsqueeze(1)).squeeze(1)  # (num_tiles, embed_dim)

        # Here we could use cross-attention, but for simplicity:
        # Concatenate map context to each action's embedding
        map_summary = map_context.mean(dim=0, keepdim=True)  # (1, embed_dim)
        action_context = action_emb + map_summary  # broadcast map info

        # Encode actions with context
        action_context = self.action_encoder(action_context.unsqueeze(1)).squeeze(1)  # (num_actions, embed_dim)

        # Score each action
        action_scores = self.action_head(action_context).squeeze(-1)  # (num_actions,)
        value = self.value_head(map_summary)  # (1, 1)

        return action_scores, value
    


def train_model():
    num_games = 100
    env_state = MLEnv()
    player_id = env_state.current_player_id  # Or similar
    tokens, attn_mask, candidates, action_mask = tokenize_game(env_state, player_id)
    tile_tokens = [t for t in tokens if t["token_type"] == 0]
    action_tokens = [t for t in tokens if t["token_type"] == 1]
    tile_dim = len(token_to_vector(tile_tokens[0]))
    action_dim = len(token_to_vector(action_tokens[0]))
    #map_feats = torch.tensor([token_to_vector(t) for t in tile_tokens], dtype=torch.float32)
    #action_feats = torch.tensor([token_to_vector(t) for t in action_tokens], dtype=torch.float32)

    model = GameTransformer(tile_dim=tile_dim, action_dim=action_dim)
    optimizer = torch.optim.Adam(model.parameters(), lr=3e-4)

    for game in range(num_games):
        done = False

        ep_rewards = []
        ep_log_probs = []
        ep_values = []

        while not env_state.game_win():
            print('Next loop')
            player_id = env_state.current_player_id  # Or similar

            # Encode game state
            tokens, attn_mask, candidates, action_mask = tokenize_game(env_state, player_id)
                        
            # Forward pass
            tile_tokens = [t for t in tokens if t["token_type"] == 0]
            action_tokens = [t for t in tokens if t["token_type"] == 1]
            print("# Tile tokens:", len(tile_tokens), "# Action tokens:", len(action_tokens))
            map_feats = torch.tensor([token_to_vector(t) for t in tile_tokens], dtype=torch.float32)
            action_feats = torch.tensor([token_to_vector(t) for t in action_tokens], dtype=torch.float32)
            print("Before")
            logits, value = model(map_feats, action_feats)
            print("After")

            # Mask invalid actions before softmax
            masked_logits = logits.clone()
            action_mask = torch.tensor(action_mask, dtype=torch.bool)
            masked_logits[~action_mask] = -1e9

            probs = torch.softmax(masked_logits, dim=-1)
            dist = torch.distributions.Categorical(probs)
            action_idx = dist.sample()

            # Step environment
            chosen_action = candidates[action_idx.item()]
            print(tokens[chosen_action])
            next_state, reward, done, _ = env_state.next_action(tokens[chosen_action])

            # Store experience
            ep_rewards.append(reward)
            ep_log_probs.append(dist.log_prob(action_idx))
            ep_values.append(value.squeeze())

        # End of episode — compute returns & advantages
        returns = compute_returns(ep_rewards, gamma=0.99)
        values = torch.stack(ep_values)
        log_probs = torch.stack(ep_log_probs)

        advantage = returns - values

        # Losses
        policy_loss = -(log_probs * advantage.detach()).mean()
        value_loss = advantage.pow(2).mean()
        loss = policy_loss + 0.5 * value_loss

        # Optimizer step
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        print(f"Game {game} — Loss: {loss.item():.4f}")


def tokenize_game(env_state, player_id):
    terrain_dict = {"Flat": 0, "Hill": 1, "Mountain": 2}
    feature_dict = {"Forest": 0}
    rivers_dict = {"W": 0, "NW": 1, "NE": 2, "E": 3, "SE": 4, "SW": 5}
    unit_type_dict = {"Melee": 0, "Ranged": 1, "Cavalry": 2}
    
    EMPTY_UNIT_TYPE = len(unit_type_dict)     # e.g., 3
    EMPTY_OWNER = 2                           # 0=me,1=enemy,2=no unit
    
    current_player = env_state.game_state.players.get_player(player_id)
    revealed_tiles = current_player.revealed_tiles
    visibile_tiles = current_player.visible_tiles
    action_tokens_indexes = []
    tokens = []
    enemy_attackable_tiles = Actions.get_enemy_attackable_tiles_coord(player_id, env_state.game_state)

    for row in range(ROWS): 
        for column in range(COLUMNS):     
            x, y, z = utils.coord_to_hex_coord(row, column)
            tile = env_state.map.tiles[(x, y, z)]
            revealed = 1 if (x, y, z) in revealed_tiles else 0
            visible = 1 if (x, y, z) in visibile_tiles else 0
            terrain_id = terrain_dict.get(tile.terrain, 0) if revealed else 0
            feature_id = feature_dict.get(tile.feature, 0) if revealed else 0

            feat_vec = [revealed] + [visible] + [1 if revealed and tile.rivers[dir] else 0 for dir in rivers_dict.keys()]

            if tile.unit_id is not None:
                unit = env_state.game_state.units.get_unit(tile.unit_id)
                unit_type = unit_type_dict[unit.type]
                owner = 0 if unit.owner_id == player_id else 1
                health = unit.health
                total_movement = unit.movement
                movement_left = unit.remaining_movement
                fortified = 1 if unit.fortified else 0
                attackable_by = enemy_attackable_tiles.get((x, y, z), []) if owner == 0 else []
            else:
                unit_type = EMPTY_UNIT_TYPE
                owner = EMPTY_OWNER
                health = 0.0
                total_movement = 0.0
                movement_left = 0.0
                fortified = 0
                attackable_by = []

            tokens.append({
                "token_type": 0,            # TILE_UNIT
                "coord_x": column,
                "coord_y": row,
                "terrain_type": terrain_id,
                "feature_type": feature_id,
                "feat_vec": feat_vec,
                "type": unit_type,          # Unit type
                "health": health,           # Unit health
                "total_movement": total_movement,
                "movement_left": movement_left,
                "fortified": fortified,
                "attackable_by": attackable_by,     #Tile attackable by enemy units
                "owner": owner
            })
            if owner == 0:
                legal_actions = Actions.get_actions(player_id, env_state.game_state)
                for action in legal_actions:
                    action_tokens_indexes.append(len(tokens))
                    if action.type == "Move":
                        action_id = 0
                        target_column, target_row = utils.hex_coord_to_coord(*action.target)
                        if action.next_tile != None:
                            destination_column, destination_row = utils.hex_coord_to_coord(*action.next_tile)
                        else:
                            destination_column, destination_row = target_column, target_row
                        axial_path = []
                        for coord in action.path:
                            axial_path.append(utils.hex_coord_to_coord(*coord))
                        tokens.append({
                            "token_type": 1,     #ACTION
                            "action_type": action_id,
                            "combat_type": 2,
                            "coord_x": column,
                            "coord_y": row,
                            "target_x": target_column,
                            "target_y": target_row,
                            "dest_x": destination_column,
                            "dest_y": destination_row,
                            "path": axial_path,
                            "damage_dealt": 0,
                            "damage_taken": 0,
                            "prob_unit_killed": 0,
                            "prob_enemy_killed": 0,
                        })
                    elif action.type == "Swap":
                        action_id = 1
                        target_column, target_row = utils.hex_coord_to_coord(*action.target)
                        tokens.append({
                            "token_type": 1,     #ACTION
                            "action_type": action_id,
                            "combat_type": 2,
                            "coord_x": column,
                            "coord_y": row,
                            "target_x": target_column,
                            "target_y": target_row,
                            "dest_x": target_column,
                            "dest_y": target_row,
                            "path": [],
                            "damage_dealt": 0.0,
                            "damage_taken": 0.0,
                            "prob_unit_killed": 0.0,
                            "prob_enemy_killed": 0.0,
                        })
                    elif action.type == "Attack":
                        action_id = 2
                        friendly_tile = env_state.game_state.map.get_tile_hex(*action.unit.coord)
                        friendly_unit = action.unit
                        enemy_tile = env_state.game_state.map.get_tile_hex(*action.target)
                        enemy_unit = env_state.game_state.units.get_unit(enemy_tile.unit_id)

                        damage_inflicted, damage_taken = CombatManager.estimate_combat(friendly_unit, enemy_unit, friendly_tile, enemy_tile, friendly_unit.combat_type)
                        unit_killed_prob, enemy_killed_prob = CombatManager.combat_death_probability(friendly_unit, enemy_unit, friendly_tile, enemy_tile, friendly_unit.combat_type)

                        if friendly_unit.combat_type == "melee":
                            full_path = UnitUtils.A_star(friendly_unit, action.target, env_state.game_state, False, True)
                            current_player = env_state.game_state.players.get_player(friendly_unit.owner_id)
                            revealed_tiles = current_player.revealed_tiles
                            visibile_tiles = current_player.visible_tiles
                            tile_before = None
                            if action.target in full_path:
                                movement_left = friendly_unit.remaining_movement
                                for x in range(len(full_path)):
                                    tile = env_state.game_state.map.get_tile_hex(*full_path[x])
                                    enter_ZOC = UnitUtils.zone_of_control(friendly_unit, tile.get_coords(), env_state.game_state)
                                    if enter_ZOC and tile.get_coords() != friendly_unit.coord:
                                        tile_before = tile.get_coords()
                                        break
                                    tile_before = tile.get_coords()
                                    current_player.update_visibility()
                                    
                                    next_tile = env_state.game_state.map.get_tile_hex(*full_path[x + 1])
                                    
                                    if next_tile.get_coords() == action.target:
                                        tile_before = tile.get_coords()
                                        break


                                    direction = utils.get_relative_position(tile.get_coords(), next_tile.get_coords())
                                    direction = utils.OPPOSITE_EDGES[direction]

                                    
                                    next_tile_movement = min(friendly_unit.movement, next_tile.get_movement(direction))
                                    

                                    
                                    if movement_left - next_tile_movement < 0:
                                        tile_before = tile.get_coords()
                                        break
                                    else:
                                        movement_left -= next_tile_movement
                            destination_column, destination_row = utils.hex_coord_to_coord(*tile_before)
                        else:
                            destination_column, destination_row = (target_column, target_row)

                        target_column, target_row = utils.hex_coord_to_coord(*action.target)
                        tokens.append({
                            "token_type": 1,     #ACTION
                            "action_type": action_id,
                            "combat_type": 0 if friendly_unit.combat_type == "melee" else 1,
                            "coord_x": column,
                            "coord_y": row,
                            "target_x": target_column,
                            "target_y": target_row,
                            "dest_x": destination_column,
                            "dest_y": destination_row,
                            "path": [],
                            "damage_dealt": damage_inflicted,
                            "damage_taken": damage_taken,
                            "prob_unit_killed": unit_killed_prob,
                            "prob_enemy_killed": enemy_killed_prob,
                        })
                    elif action.type == "Fortify":
                        action_id = 3
                        #target_column, target_row = utils.hex_coord_to_coord(*action.target)
                        tokens.append({
                            "token_type": 1,     #ACTION
                            "action_type": action_id,
                            "combat_type": 2,
                            "coord_x": column,
                            "coord_y": row,
                            "target_x": column,
                            "target_y": row,
                            "dest_x": column,
                            "dest_y": row,
                            "path": [],
                            "damage_dealt": 0.0,
                            "damage_taken": 0.0,
                            "prob_unit_killed": 0.0,
                            "prob_enemy_killed": 0.0,
                        })
    attn_mask = [1] * len(tokens)
    action_mask = [0] * len(action_tokens_indexes)
    #for i in action_tokens_indexes:
    #    action_mask[i] = 1

    return tokens, attn_mask, action_tokens_indexes, action_mask

            # type (move, attack, heal, etc.)
            # target (coord of target (move destination or attackable unit))
            # Turns to reach (if applicable)
            # Unit id? (need to connect this so it knows what unit is completing action)

def token_to_vector(token):
    if token["token_type"] == 0:  # TILE
        return [
            0,  # token_type: TILE
            token.get("terrain_type", 0),
            token.get("feature_type", 0),
            token.get("owner", -1),
            token.get("city_present", 0),
            token.get("unit_present", 0),
            token.get("coord_x", 0),
            token.get("coord_y", 0),
            0, 0, 0, 0, 0, 0, 0, 0
        ]
    elif token["token_type"] == 1:  # ACTION
        return [
            1,  # token_type: ACTION
            token.get("action_type", 0),
            token.get("combat_type", 0),
            token.get("coord_x", 0),
            token.get("coord_y", 0),
            token.get("target_x", 0),
            token.get("target_y", 0),
            token.get("dest_x", 0),
            token.get("dest_y", 0),
            token.get("damage_dealt", 0),
            token.get("damage_taken", 0),
            float(token.get("prob_unit_killed", 0)),
            float(token.get("prob_enemy_killed", 0)),
            0, 0, 0
        ]
    else:
        raise ValueError(f"Unknown token type: {token['token_type']}")
train_model()