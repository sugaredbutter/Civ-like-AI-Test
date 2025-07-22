moveScore = dict(
    exp_unrevealed = 20,
    exp_nonvisible = 5,
    exp_org_destination = 10,

    

    off_mult = 1,                   #Consider unit health
    off_attackable_enemy_units = 50,
    off_adj_enemy_units = 20,
    off_damage_mult = 1,

    def_mult = 1,
    def_num_attackable_by_penalty = 50,
    def_adjacent_friendlies = 5,
    def_defensive_bonus = 10,
    def_damage_taken_mult = 1,
    def_damage_inflicted_mult = 1,

    dist_move_penalty_alpha = 0.1,
)

attackScore = dict(
    combat_mult = 3,
    combat_health_aggro = 200,
    combat_kill_bonus = 100,
    combat_death_penalty = 200,
    combat_ally_bonus_mult_bonus = 2.3,
    combat_enemy_bonus_mult_penalty = 1.5,
    combat_damage_mult = 2,

)

fortifyScore = dict(
    fortify_mult = 2,
    fortify_continued = 20,
    fortify_not_full = 40,
    fortify_full_penalty = 20
)
