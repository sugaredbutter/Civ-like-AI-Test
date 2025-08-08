units = {
    "Melee": {
        "health": 100,
        "attack": 20,
        "defense": 20,
        "movement": 2,
        "visibility": 2,
        "fortified": 3,
        "defense_zoc": True,
        "attack_zoc": True,
        "combat_type": "melee"
    },
    "Ranged": {
        "health": 100,
        "attack": 25,
        "defense": 20,
        "movement": 2,
        "visibility": 2,
        "range": 2,
        "fortified": 3,
        "defense_zoc": False,
        "attack_zoc": True,
        "melee_attack_defensive_debuff": .25, #Percentage (25% debuff)
        "combat_type": "ranged"        
        
    },
    "Cavalry": {
        "health": 100,
        "attack": 30,
        "defense": 20,
        "movement": 4,
        "visibility": 2,
        "fortified": 2,
        "defense_zoc": True,
        "attack_zoc": False,
        "combat_type": "melee"
    }
}