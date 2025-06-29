biomes = {
    "Plain": {
        "biome_color": (100, 200, 100),
        "hover_color": (150, 255, 150),
        "Terrain": {
            "Hill": {
                "terrain_color": (38, 145, 38),
                "hover_color": (61, 196, 61),
                "movement": 2,
                "visibility_penalty": 2,
                "visibility_bonus": 2
            },
            "Mountain": {
                "terrain_color": (71, 70, 70),
                "hover_color": (92, 92, 92),
                "movement": -1,
                "visibility_penalty": float("inf"),
                "visibility_bonus": 2

            },
            "Flat": {
                "movement": 0,
                "visibility_penalty": 1, 
                "visibility_bonus": 0
            }
        },
        "Feature": {
            "Forest": {
                "movement": 2,
                "visibility_penalty": 2,
                "visibility_bonus": 0
            }
        }
    },
    "Desert": {
        "biome_color": (199, 192, 0),
        "hover_color": (252, 245, 45),
        "movement": 1,
        "Terrain": {
            "Hill": {
                "terrain_color": (173, 157, 7),
                "hover_color": (204, 186, 12),
                "movement": 2,
                "visibility_penalty": 2,
                "visibility_bonus": 2

            },
            "Mountain": {
                "terrain_color": (82, 57, 8),
                "hover_color": (191, 131, 13),
                "movement": -1,
                "visibility_penalty": float("inf"),
                "visibility_bonus": 2
            },
            "Flat": {
                "movement": 0,
                "visibility_penalty": 1,
                "visibility_bonus": 0
            }
        },
        "Feature": {
            "Forest": {
                "movement": 2,
                "visibility_penalty": 2,
                "visibility_bonus": 0
            }
        }
    }
}
features = {
    "River": {
        "feature_color": (30, 43, 230),
        "movement": 2
    }
}