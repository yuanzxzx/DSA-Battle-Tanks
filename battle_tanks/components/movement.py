#imports
import pygame as pg
from typing import Union
from battle_tanks.components.network import NetworkComponent
from battle_tanks.sprites import Player
from battle_tanks.commons.package import Struct


class MovementComponent:
#
    def __init__(self, network: Union[NetworkComponent,None], player:Player):
        self.network = network
        self.player = player

    #Translates input into movement
    def keys(self): #Designates keys with iput for movement
        key = pg.key.get_pressed()
        actions = []
        if key[pg.K_d]:
            action = Struct.LEFT_EVENT_PLAYER
            actions.append(action)
        elif key[pg.K_a]:
            action = Struct.RIGHT_EVENT_PLAYER
            actions.append(action)
        elif key[pg.K_w]:
            action = Struct.UP_EVENT_PLAYER
            actions.append(action)
        elif key[pg.K_s]:
            action = Struct.DOWN_EVENT_PLAYER
            actions.append(action)
        if key[pg.K_i]:
            action = Struct.RIGHT_ANGLE_EVENT_PLAYER
            actions.append(action)
        elif key[pg.K_p]:
            action = Struct.LEFT_ANGLE_EVENT_PLAYER
            actions.append(action)

        # network transmission (queues action pressed to be processed on a server if internet connection is present)
        if self.network and len(actions) > 0:
            self.network.send_keys(actions) 
