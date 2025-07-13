import pygame

class AssetManager:
    def __init__(self):
        self.trees = {1: pygame.image.load("Assets/Trees/Tree_1.png")}
        #self.plains_hex = pygame.image.load("Assets/Trees/hex_template.png")
        self.red_icon = {
            "Melee": pygame.image.load("Assets/Units/Red/red_melee.png"),
            "Ranged": pygame.image.load("Assets/Units/Red/red_archer.png"),
            "Cavalry": pygame.image.load("Assets/Units/Red/red_cavalry.png")
        }
        self.purple_icon = {
            "Melee": pygame.image.load("Assets/Units/Purple/purple_melee.png"),
            "Ranged": pygame.image.load("Assets/Units/Purple/purple_archer.png"),
            "Cavalry": pygame.image.load("Assets/Units/Purple/purple_cavalry.png")
        }
        self.green_icon = {
            "Melee": pygame.image.load("Assets/Units/Green/green_melee.png"),
            "Ranged": pygame.image.load("Assets/Units/Green/green_archer.png"),
            "Cavalry": pygame.image.load("Assets/Units/Green/green_cavalry.png")
        }
        self.blue_icon = {
            "Melee": pygame.image.load("Assets/Units/Blue/blue_melee.png"),
            "Ranged": pygame.image.load("Assets/Units/Blue/blue_archer.png"),
            "Cavalry": pygame.image.load("Assets/Units/Blue/blue_cavalry.png")
        }
    
    def get_icon(self, color, type):
        if color == "red":
            return self.red_icon.get(type, None)
        if color == "purple":
            return self.purple_icon.get(type, None)
        if color == "green":
            return self.green_icon.get(type, None)
        if color == "blue":
            return self.blue_icon.get(type, None)
