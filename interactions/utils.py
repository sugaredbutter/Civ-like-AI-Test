import math
import interactions.config as config

def click_to_hex(pos_x, pos_y):
    pos_x -= config.map_settings["offsetX"] - config.hex["inner_radius"]
    pos_y -= config.map_settings["offsetY"] - config.hex["radius"]
    pos_y = config.map_settings["pixel_height"] - pos_y - 1
    x = pos_x / (config.hex["inner_radius"] * 2) - 1 
    y = -x
    offset = pos_y / (config.hex["radius"] * 3)
    x -= offset
    y -= offset
    
    iX = round(x)
    iY = round(y)
    iZ = round(-x -y)

    if iX + iY + iZ != 0:
        dX = abs(x - iX)
        dY = abs(y - iY)
        dZ = abs(-x -y - iZ)
        if dX > dY and dX > dZ:
            iX = -iY - iZ
            
        elif (dZ > dY):
            iZ = -iX - iY
        elif (dY > dX and dY > dZ):
            iY = -iX - iZ
        else:
            iX = -iY - iZ
            
    return (iX, iY, iZ)

def coord_to_hex_coord(row, column):
    x = row - int(column / 2)
    y = -x - column
    z = column
    return (x, y, z)
    