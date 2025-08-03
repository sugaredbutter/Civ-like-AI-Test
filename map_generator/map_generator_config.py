scale = .4
octaves = 4
persistence = 0.5
lacunarity = 2.0
seed = 1
MapConfig = dict(
    #Terrain/elevation
    elevation = 2, # Need to implement  #Higher elevation = More mountains and hills
    mountainous = 2, # Need to implement  #Higher mountainous = More mountains (lowers mountain threshold)
    hilliness = 2, # Need to implement  #Higher hilliness = More hills (lowers hill threshold and < mountain threshold)
    #For example, less hilliness and more mountainous should mean more flatland and more mountains

    variability = 2, #Octaves, basically clumpiness?             
    #Biomes
    temperature = 2,        #Mix between desert and grassland   
    biome_scale = 2,        #How large each biome is

    #Features/Forests
    moisture = 2,           #More moisture = More forests
    clumpiness = 2,         #How clumped are forests
    seed = ''
)
        
