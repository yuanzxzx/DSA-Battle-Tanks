""" This is the Player [Tank] """
import math
import os

import pygame as pg
from .cannon import Cannon
from battle_tanks.commons.municion import CannonType

from typing import Callable


class Player(Cannon): # Player class
    """ This class represents to tank (more cannon) """
    SPEED = 2 # Speed of player
    ANGLE = 5 # Angle of player
    ANGLE_RIGHT = 1 # Angle of player right
    ANGLE_LEFT = -1 # Angle of player left
    SIZE_BODY_RECT = (32,32)
    DAMAGE =  10
    MAX_DAMAGE = 100

    TELESCOPIC_SIGH = pg.image.load(os.path.join(os.path.abspath("."), "assets/images/telescopic_sight.png")) # Image of telescopic sigh

    def __init__(self, position: tuple, number: int, cannon_type: dict, tank_color: int = 0): # Initial position, number, cannon type and tank color
        super().__init__(position, cannon_type)
        self.player_number = number # Player number
        self.tank_color = tank_color
        self.name = f"Player {number}" # Default name
        self.damage = 0 # Damage of player
        self.fire = False # Fire of player
        self.angle = 0 # Angle of player
        self.angle_cannon = 0 # Angle of cannon
        self.type_gun = cannon_type # Cannon type
        
        self.image = pg.Surface((32, 32), pg.SRCALPHA) # Image of player
        self.rect = self.image.get_rect()
        self.rect.x = position[0] # Position x of player
        self.rect.y = position[1] # Position y of player

        self.body_rect = pg.Rect(0, 0, 32, 32) # Rect of player
        self.body_rect.center = self.rect.center

        self.vl = 3
        self.vlx = 0
        self.vly = 0
        self._life = 10
        self._dead = False
        
        self.laser_active = False # Laser active of player
        self.laser_energy = 100 # Laser energy of player


    @staticmethod # Static method
    def rotate_external(xbool, angle, surface, rect): # Rotates the player around 360
        angle += Player.ANGLE * xbool
        if math.sqrt(angle ** 2) >= 360:
            angle = 0
        surface = pg.transform.rotate(surface, angle)
        rect = pg.Rect(rect.topleft, surface.get_size())
        rect.center = rect.center
        return angle, rect


    def update(self):
        """ Update the position of the player and cannon"""   
        self.body_rect.center = self.rect.center
        self.rect_cannon.center = self.body_rect.center


    def rotate_rect(self,xbool,surface):
        """Rotate the rect player around"""
        self.angle += 10 * xbool
        angle = math.sqrt(self.angle**2)
        if angle >= 360:
            self.angle = 0
        surface = pg.transform.rotate(surface,self.angle)
        rect = pg.Rect(self.rect.topleft,surface.get_size())
        rect.center = self.rect.center
        self.rect = rect


    @staticmethod # Static method
    def draw(surface,angle): # Draw the player
        return pg.transform.rotate(surface,angle)


    @property 
    def damage(self): # Property of damage
        """ return damage """
        return self._damage


    @damage.setter # Setter of damage
    def damage(self, value:float):
        """setter for damage"""
        self._damage = value


    @property
    def fire(self): # Property of Fire
        """ return fire """
        return self._fire


    @fire.setter
    def fire(self, value:bool): # Fire Setter
        """ setter for fire """
        self._fire = value
        if self._fire is True:
            self.type_gun.count_available -=1


    def telescopic_sight(self): 
        """ Draw the telescopic sight """
        return {
                "x": self.rect.x,
                "y": self.rect.y,
                "angle_cannon": self.angle_cannon,
        }

    def __str__(self): 
        return f"---NUMBER: [{self.player_number}  ---POS: [{self.rect.center}] ---DAMAGE: {self._damage}"
