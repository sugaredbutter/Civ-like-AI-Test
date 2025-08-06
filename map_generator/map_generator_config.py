scale = .3
octaves = 10
persistence = 0.5
lacunarity = 2.0
seed = 1
MapConfig = dict(
    #Terrain/elevation
    elevation_scale = dict(
        default = 5,
        current = 5,
        min_val = 1,
        max_val = 10,

    ), 

    elevation = dict(
        default = 3,
        current = 3,
        min_val = 1,
        max_val = 5,

    ), 
    
    # Need to implement  #Higher elevation = More mountains and hills
    mountainous = dict(
        default = 3,
        current = 3,
        min_val = 1,
        max_val = 5,

    ), 
    
    
    # Need to implement  #Higher mountainous = More mountains (lowers mountain threshold)
    hilliness = dict(
        default = 3,
        current = 3,
        min_val = 1,
        max_val = 5,

    ),
    
    
    # Need to implement  #Higher hilliness = More hills (lowers hill threshold and < mountain threshold)
    #For example, less hilliness and more mountainous should mean more flatland and more mountains

    variability = dict(
        default = 3,
        current = 3,
        min_val = 1,
        max_val = 10,

    ), #Octaves, basically clumpiness?             
    #Biomes
    temperature = dict(
        default = 3,
        current = 3,
        min_val = 1,
        max_val = 5,

    ),        #Mix between desert and grassland   
    biome_scale = dict(
        default = 4,
        current = 4,
        min_val = 1,
        max_val = 7,

    ),        #How large each biome is

    #Features/Forests
    moisture = dict(
        default = 3,
        current = 3,
        min_val = 1,
        max_val = 5,

    ),           #More moisture = More forests
    clumpiness = dict(
        default = 3,
        current = 3,
        min_val = 1,
        max_val = 5,

    ),         #How clumped are forests

    rivers = dict(
        default = 3,
        current = 3,
        min_val = 1,
        max_val = 5,

    ),
    seed = ''
)
Terrain = dict(
    scale = dict(
        level = .3,
        change = .05
    ),
    elevation = dict(
        level = 0,
        change = .05,
    ),
    hill = dict(
        level = 0,
        change = -.05,
    ),
    mountain = dict(
        level = .2,
        change = -.05,
    ),
)
Biome = dict(
    scale = dict(
        level = .3,
        change = .05
    ),
    temperature = dict(
        level = 0,
        change = .1,
    ),
    plain = dict(
        level = .1,
        change = .1,
    ),
)
Feature = dict(
    scale = dict(
        level = .5,
        change = .2
    ),
    moisture = dict(
        level = 0,
        change = .1,
    ),
    forest = dict(
        level = .1,
        change = -.1,
    ),
    river = dict(
        level = 20,
        change = 10,
    )
)


        
