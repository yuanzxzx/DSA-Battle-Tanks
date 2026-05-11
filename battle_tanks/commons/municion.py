
""" MANAGEMENT OF THE MUNICION """

from typing import  List,Tuple
import pygame as pg
from battle_tanks.commons.tank_surface import draw_bullet

class CannonType:
    def __init__(self, count, gun_type, size: Tuple[int, int]):
        """
        Constructor — initializes the cannon's ammunition state.
        Parameters:
            count     (int)           : Cannon bullets
            gun_type  (dict)          : Cannon properties
            size      (Tuple[int,int]): Bullet size.
        """
        self.count = count # Maximum bullet capacity.
        self.count_available = count # Current bullets remaining (starts full).
        self.type: dict = gun_type # Gun metadata dict.
        self.limit = False # Flag for whether ammo is limited (unused/False by default).
        self.vl = None # Velocity or value placeholder (not yet assigned).
        self.size = size # Bullet icon size for rendering.
        self.damage = None # Damage value (not yet assigned).
        self.reload_time = 100 # Number of ticks to wait before reloading (100 ticks).
        self.count_reload = 0 # Counter that tracks elapsed ticks since ammo hit 0.

    @property
    def count_available(self):
        return self.count_available

    @count_available.setter
    def count_available(self, count_available): # Updates the current number of available bullets.
        self.count_available = count_available

    def render(self, bullet_surface: pg.Surface) -> pg.Surface: #draws bullet
        """
            How it works:
            1. Calculates position for each bullet icon based on icon width,
               placing them side-by-side: [(0,0), (width,0), (2*width,0), ...].
            2. If ammo has reached 0, it starts incrementing the reload counter
               (count_reload) each time this method is called (once per game tick).
            3. Once the reload counter reaches reload_time (100 ticks), it resets
               the counter and restores count_available back to the full count.
            4. Iterates over the computed bullet positions and calls draw_bullet()
               to render each bullet icon onto bullet_surface.
        """
        width = self.size[0]
        bullets = [(width * i, 0) for i in range(0, self.count_available)] #calculate position for each bullet icon based on icon width 

        if self.count_available <= 0: #if no bullets left, start reload counter
            self.count_reload += 1

        if self.count_available <= 0 and self.count_reload >= self.reload_time: #if reload time is reached, reset counter and add bullets
            self.count_reload = 0
            self.count_available = self.count

        for bullet in bullets: #draw bullet
            draw_bullet(bullet_surface, bullet, 0, (4, 10)) 

        return bullet_surface
