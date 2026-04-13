import pygame as pg
import math
from battle_tanks.commons.tank_surface import draw_bullet

class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, angle, speed=7):
        super().__init__()
        # Use the existing drawing helper from the project
        self.image = draw_bullet() 
        self.rect = self.image.get_rect(center=(x, y))
        
        # Calculate direction
        # In this game, 0 degrees is Up. math.radians needs adjustment.
        rad = math.radians(-angle)
        self.vx = math.sin(rad) * speed
        self.vy = -math.cos(rad) * speed # Negative because Y increases downwards

    def update(self):
        # Move the bullet
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        # Simple boundary check: kill bullet if it leaves the screen area
        if not (0 <= self.rect.x <= 2000 and 0 <= self.rect.y <= 2000):
            self.kill()
