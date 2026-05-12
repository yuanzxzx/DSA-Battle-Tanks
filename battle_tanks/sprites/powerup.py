import pygame as pg
import math
import random

class PowerUp(pg.sprite.Sprite): # Power Up Class
    SIZE = 24
    PULSE_SPEED = 0.05

    def __init__(self, x: int, y: int): # Initial position of power up
        super().__init__()
        self.world_x = x
        self.world_y = y
        self._pulse = 0

        self.base_image = pg.Surface((self.SIZE, self.SIZE), pg.SRCALPHA) # creates image for power up
        # Draw a mine icon — dark circle with exclamation
        pg.draw.circle(self.base_image, (40, 40, 40), (12, 12), 12) # Dark circle for power up
        pg.draw.circle(self.base_image, (200, 50, 50), (12, 12), 10) # Red circle for power up
        font = pg.font.SysFont(None, 22)
        label = font.render("!", True, (255, 255, 255)) # Creates exclamation mark for power up
        self.base_image.blit(label, (9, 2))

        self.image = self.base_image.copy() # Copies the image of the power up
        self.rect = self.image.get_rect(topleft=(x, y)) # Gets the position of the power up

    def update(self, *args): # Updates the power up
        self._pulse += self.PULSE_SPEED # Adds pulse speed to the power up
        scale = 1.0 + 0.15 * math.sin(self._pulse) # Creates a pulse effect for power up
        size = int(self.SIZE * scale) # Scales the size of the power up
        self.image = pg.transform.scale(self.base_image, (size, size)) # Scales the image of the power up
        self.rect = self.image.get_rect(center=(self.world_x + 12, self.world_y + 12)) # Centers the power up