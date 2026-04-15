import pygame as pg
import math
import random

class PowerUp(pg.sprite.Sprite):
    SIZE = 24
    PULSE_SPEED = 0.05

    def __init__(self, x: int, y: int):
        super().__init__()
        self.world_x = x
        self.world_y = y
        self._pulse = 0

        self.base_image = pg.Surface((self.SIZE, self.SIZE), pg.SRCALPHA)
        # Draw a mine icon — dark circle with exclamation
        pg.draw.circle(self.base_image, (40, 40, 40), (12, 12), 12)
        pg.draw.circle(self.base_image, (200, 50, 50), (12, 12), 10)
        font = pg.font.SysFont(None, 22)
        label = font.render("!", True, (255, 255, 255))
        self.base_image.blit(label, (9, 2))

        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, *args):
        self._pulse += self.PULSE_SPEED
        scale = 1.0 + 0.15 * math.sin(self._pulse)
        size = int(self.SIZE * scale)
        self.image = pg.transform.scale(self.base_image, (size, size))
        self.rect = self.image.get_rect(center=(self.world_x + 12, self.world_y + 12))