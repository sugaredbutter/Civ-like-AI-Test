import interactions.utils as utils
import pygame
import math
import config

class VisualEffectHandler:
    def __init__(self, screen):
        self.screen = screen

        self.damage_manager = DamageEffects(screen)
        pass

    def add_damage(self, damage, tile_coord, enemy):
        color = (212, 20, 6) if enemy else (255, 255, 255)
        self.damage_manager.add_damage(damage, tile_coord, color, 1)

    def display_visuals(self):
        self.damage_manager.display_damage()

class DamageEffects:
    def __init__(self, screen):
        self.screen = screen
        self.solid_duration = 60 * 3
        self.fade_duration = 60 * 3
        self.damage = []
        self.font = pygame.font.SysFont(None, 24)

    def add_damage(self, damage, tile_coord, color, lifetime):
        self.damage.append([math.ceil(-damage), tile_coord, color, lifetime])

    def display_damage(self):
        i = 0
        hex_radius = config.hex["radius"]
        while i < len(self.damage):
            damage, tile_coord, color, lifetime = self.damage[i]
            
            axial_coord = utils.hex_coord_to_coord(*tile_coord)
            tile_pixel_x, tile_pixel_y = utils.coord_to_pixel(*axial_coord)
            tile_pixel_x += hex_radius/2
            tile_pixel_y -= hex_radius/2
            tile_pixel_coord = (tile_pixel_x, tile_pixel_y)
            text_surf = self.font.render(str(damage), True, color)
            if lifetime < self.solid_duration:
                alpha = 255
            elif lifetime < self.solid_duration + self.fade_duration:
                fade_progress = (lifetime - self.solid_duration) / self.fade_duration
                alpha = max(0, int(255 * (1 - fade_progress)))
            else:
                alpha = 0
            text_surf.set_alpha(alpha)
            self.screen.blit(text_surf, tile_pixel_coord)
            if lifetime > self.solid_duration + self.fade_duration:
                del self.damage[i]
            else:
                self.damage[i][3] += 1
                i += 1




