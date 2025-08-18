import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import Adam

import utils as utils
import config as config
from machine_learning.environment_setup import MLEnv
from Agents.actions import Actions
from Agents.actions import CompleteUnitAction
from Agents.agent import ScoreAgent
from combat_manager.combat_manager import CombatManager
from units.units_utils import UnitUtils
import random
import copy
from logs.logging import LoggingML
from logs.logging import Logging


import pynvml
import psutil
import gc
# Initialize NVML
pynvml.nvmlInit()

ROWS, COLUMNS = config.map_settings["tile_height"], config.map_settings["tile_width"]


# Reference
import torch.utils.checkpoint as checkpoint

class GameTransformer(nn.Module):
    def __init__(self, tile_dim, action_dim, embed_dim=128, nhead=4, num_layers=2):
        super().__init__()
        self.tile_embed = nn.Linear(tile_dim, embed_dim)
        self.action_embed = nn.Linear(action_dim, embed_dim)

        encoder_layer = nn.TransformerEncoderLayer(d_model=embed_dim, nhead=nhead)
        self.map_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        cross_layer = nn.TransformerEncoderLayer(d_model=embed_dim, nhead=nhead)
        self.action_encoder = nn.TransformerEncoder(cross_layer, num_layers=num_layers)
        
        self.action_head = nn.Linear(embed_dim, 1)
        self.value_head = nn.Linear(embed_dim, 1)

    def forward(self, map_feats, action_feats):
        map_emb = self.tile_embed(map_feats)
        action_emb = self.action_embed(action_feats)

        # Gradient checkpointing for encoders
        map_context = checkpoint.checkpoint(self.map_encoder, map_emb.unsqueeze(1)).squeeze(1)
        map_summary = map_context.mean(dim=0, keepdim=True)
        action_context = action_emb + map_summary
        action_context = checkpoint.checkpoint(self.action_encoder, action_context.unsqueeze(1)).squeeze(1)

        action_scores = self.action_head(action_context).squeeze(-1)
        value = self.value_head(map_summary)
        return action_scores, value
    


def train_model():
    num_games = 2000
    env_state = MLEnv()
    player_id = env_state.current_player_id  # Or similar
    tokens, attn_mask, candidates, action_mask = tokenize_game(env_state, player_id)
    tile_tokens = [t for t in tokens if t["token_type"] == 0]
    action_tokens = [t for t in tokens if t["token_type"] == 1]
    tile_dim = len(token_to_vector(tile_tokens[0]))
    action_dim = len(token_to_vector(action_tokens[0]))
    #map_feats = torch.tensor([token_to_vector(t) for t in tile_tokens], dtype=torch.float32)
    #action_feats = torch.tensor([token_to_vector(t) for t in action_tokens], dtype=torch.float32)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = GameTransformer(tile_dim=tile_dim, action_dim=action_dim).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=3e-4)

    num_model_checkpoints = 5
    model_checkpoints = [copy.deepcopy(model)]
    for game in range(num_games):
        print("New Game")
        done = False

        ep_rewards = []
        ep_log_probs = []
        ep_values = []
        other_player_models = []
        
        for player_id in range(config.num_players):
            if player_id == 0:
                other_player_models.append(None)
            elif game < 1000:
                other_player_models.append(None)
            elif game < 1001:
                if player_id <= 2:
                    other_player_models.append(None)
                else:
                    other_player_models.append(random.choice(model_checkpoints))
            else:
                other_player_models.append(random.choice(model_checkpoints))

        AI_prev_turn = []
        turn_count = 0
        while not env_state.game_win() and turn_count < 150:
            player_id = env_state.current_player_id  # Or similar
            print(f"Turn {turn_count}, Player {player_id}")

            actions = True
            if player_id == 0:
                AI_prev_turn = []
                while actions == True:
                    # Encode game state
                    tokens, attn_mask, candidates, action_mask = tokenize_game(env_state, player_id)
                                
                    # Forward pass
                    tile_tokens = [t for t in tokens if t["token_type"] == 0]
                    action_tokens = [t for t in tokens if t["token_type"] == 1]
                    if len(action_tokens) == 0:
                        env_state.next_turn()
                        actions = False
                        continue
                    print("# Tile tokens:", len(tile_tokens), "# Action tokens:", len(action_tokens))
                    map_feats = torch.tensor([token_to_vector(t) for t in tile_tokens], dtype=torch.float32).to(device)
                    action_feats = torch.tensor([token_to_vector(t) for t in action_tokens], dtype=torch.float32).to(device)
                    logits, value = model(map_feats, action_feats)

                    # Mask invalid actions before softmax
                    masked_logits = logits.clone()
                    action_mask = torch.tensor(action_mask, dtype=torch.bool)
                    masked_logits[~action_mask] = -1e9

                    probs = torch.softmax(masked_logits, dim=-1)
                    dist = torch.distributions.Categorical(probs)
                    action_idx = dist.sample()

                    # Step environment
                    chosen_action_idx = action_idx.item()  # this is an index into action_tokens
                    chosen_action = action_tokens[chosen_action_idx]  # directly use the action token
                    reward, unit_id, target_unit_id = env_state.next_action(chosen_action)

                    # Store experience
                    ep_rewards.append(reward)
                    ep_log_probs.append(dist.log_prob(action_idx))
                    ep_values.append(value.squeeze())

                    AI_prev_turn.append((unit_id, len(ep_rewards) - 1))
                    if len(AI_prev_turn) > 0:
                        unit_action_indexes = []
                        split_reward = reward / len(AI_prev_turn)
                        for i, action in enumerate(AI_prev_turn):
                            ep_rewards[action[1]] += split_reward
                            if action[0] == unit_id:
                                unit_action_indexes.append(i)
                        if len(unit_action_indexes) > 0:
                            split_reward = reward / len(unit_action_indexes)
                            for i in unit_action_indexes:
                                ep_rewards[AI_prev_turn[i][1]] += split_reward
                        else:
                            for i, action in enumerate(AI_prev_turn):
                                ep_rewards[action[1]] += split_reward

                    del map_feats, action_feats, logits, value, masked_logits, probs, dist, action_idx
            elif other_player_models[player_id] == None:
                while actions == True:
                    actions, reward, unit_id, target_unit_id = env_state.score_choose_best_action()
                    if actions and len(AI_prev_turn) > 0:
                        unit_action_indexes = []
                        split_reward = reward / len(AI_prev_turn)
                        for i, action in enumerate(AI_prev_turn):
                            ep_rewards[action[1]] += split_reward
                            if action[0] == target_unit_id:
                                unit_action_indexes.append(i)
                        if len(unit_action_indexes) > 0:
                            split_reward = reward / len(unit_action_indexes)
                            for i in unit_action_indexes:
                                ep_rewards[AI_prev_turn[i][1]] += split_reward
                        else:
                            for i, action in enumerate(AI_prev_turn):
                                ep_rewards[action[1]] += split_reward
                env_state.next_turn()
            else:
                while actions == True:
                    player_model = other_player_models[player_id][1]

                    # Encode game state
                    tokens, attn_mask, candidates, action_mask = tokenize_game(env_state, player_id)
                                
                    # Forward pass
                    tile_tokens = [t for t in tokens if t["token_type"] == 0]
                    action_tokens = [t for t in tokens if t["token_type"] == 1]
                    if len(action_tokens) == 0:
                        env_state.next_turn()
                        actions = False
                        continue
                    print("# Tile tokens:", len(tile_tokens), "# Action tokens:", len(action_tokens))
                    map_feats = torch.tensor([token_to_vector(t) for t in tile_tokens], dtype=torch.float32).to(device)
                    action_feats = torch.tensor([token_to_vector(t) for t in action_tokens], dtype=torch.float32).to(device)
                    with torch.no_grad():
                        logits, value = player_model(map_feats, action_feats)

                    # Mask invalid actions before softmax
                    masked_logits = logits.clone()
                    action_mask = torch.tensor(action_mask, dtype=torch.bool)
                    masked_logits[~action_mask] = -1e9

                    probs = torch.softmax(masked_logits, dim=-1)
                    dist = torch.distributions.Categorical(probs)
                    action_idx = dist.sample()

                    # Step environment
                    chosen_action_idx = action_idx.item()  # this is an index into action_tokens
                    chosen_action = action_tokens[chosen_action_idx]  # directly use the action token
                    reward, unit_id, target_unit_id = env_state.next_action(chosen_action)
                    if len(AI_prev_turn) > 0:
                        unit_action_indexes = []
                        split_reward = reward / len(AI_prev_turn)
                        for i, action in enumerate(AI_prev_turn):
                            ep_rewards[action[1]] += split_reward
                            if action[0] == target_unit_id:
                                unit_action_indexes.append(i)
                        if len(unit_action_indexes) > 0:
                            split_reward = reward / len(unit_action_indexes)
                            for i in unit_action_indexes:
                                ep_rewards[AI_prev_turn[i][1]] += split_reward
                        else:
                            for i, action in enumerate(AI_prev_turn):
                                ep_rewards[action[1]] += split_reward
            torch.cuda.empty_cache()
            turn_count += 1
                        


        if env_state.winner == 0: 
            win_reward = env_state.AI_win_score
            num_actions = len(ep_rewards)
            if num_actions > 0:
                reward_per_action = win_reward / num_actions

                for i in range(num_actions):
                    ep_rewards[i] += reward_per_action
        # End of episode — compute returns & advantages
        returns = compute_returns(ep_rewards, gamma=0.99)
        values = torch.stack(ep_values)
        log_probs = torch.stack(ep_log_probs)
        returns = returns.to(device)
        values = values.to(device)
        advantage = returns - values
        advantage = (advantage - advantage.mean()) / (advantage.std() + 1e-8)

        # Losses
        policy_loss = -(log_probs * advantage.detach()).mean()
        value_loss = advantage.pow(2).mean()
        loss = policy_loss + 0.5 * value_loss

        # Optimizer step
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        info = {
            "Game": game,
            "Turns": turn_count,
            "Num_Players": config.num_players,
            "Players": env_state.player_stats,
            "Models": [None if x is None else x[0] for x in other_player_models],
            "AI_score": sum(ep_rewards),
            "Loss": f"{loss.item():.4f}",
            "Winner": env_state.winner
        }
        sys_stats = get_system_stats()

        LoggingML.log_ML_stats(info, sys_stats)
        # Example logging
        print(f"Game {game} — Loss: {loss.item():.4f}")
        if game % 5 == 0 and game != 0:
            model_checkpoints.append((game, copy.deepcopy(model)))
        if len(model_checkpoints) > num_model_checkpoints:
            model_checkpoints.pop(0)
        print("Check 1")
        torch.cuda.empty_cache()
        print("Check 2")

        gc.collect()
        print("Check 3")
        del env_state
        env_state = MLEnv()
        print("Check 4")

def compute_returns(rewards, gamma):
    returns = []
    G = 0
    for r in reversed(rewards):
        G = r + gamma * G
        returns.insert(0, G)
    return torch.tensor(returns, dtype=torch.float32)

# Quick thing to figure out random killed. Turns out wasn't memory, but just infinite for loop that occurs incredibly rarely in river generation. Fixed for now using counter limit in offending
# while loop. Not sure why its infinitely looping.
def get_system_stats():
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)  # GPU 0
    
    # GPU utilization
    utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
    gpu_load = utilization.gpu  # %
    gpu_mem = utilization.memory  # %

    # VRAM usage
    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    vram_used = mem_info.used / (1024 ** 2)  # MB
    vram_total = mem_info.total / (1024 ** 2)  # MB

    # System RAM usage
    ram = psutil.virtual_memory()
    ram_used = ram.used / (1024 ** 2)  # MB
    ram_total = ram.total / (1024 ** 2)  # MB

    return {
        "GPU Load (%)": gpu_load,
        "VRAM Used (MB)": vram_used,
        "VRAM Total (MB)": vram_total,
        "VRAM %": str(vram_used / vram_total * 100) + "%",
        "System RAM Used (MB)": ram_used,
        "System RAM Total (MB)": ram_total,
        "System RAM %": str(ram_used / ram_total * 100) + "%",
    }


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
            tile = env_state.game_state.map.tiles[(x, y, z)]
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
                    if action.type == "Move":
                        action_id = 0
                        target_column, target_row = utils.hex_coord_to_coord(*action.target)

                        #Remove ability to path to further tiles as that added too many tokens.
                        if action.next_tile != None:
                            continue
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
                            "dest_x": target_column,
                            "dest_y": target_row,
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
                        target_column, target_row = utils.hex_coord_to_coord(*action.target)

                        if friendly_unit.combat_type == "melee":
                            full_path = UnitUtils.A_star(friendly_unit, action.target, env_state.game_state, False, True)
                            current_player = env_state.game_state.players.get_player(friendly_unit.owner_id)
                            revealed_tiles = current_player.revealed_tiles
                            visibile_tiles = current_player.visible_tiles
                            tile_before = friendly_unit.coord
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
                    action_tokens_indexes.append(len(tokens))

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