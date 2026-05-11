import pytmx
import pygame as pg
import math
import pathlib
import random

from typing import Tuple, List
from collections.abc import Callable
from battle_tanks.sprites import Brick, Player, Block


class Collision: # Manages collisions and level state
    bricks = pg.sprite.Group()
    players:List[dict] = []
    size_screen:tuple = (0,0)
    lvl_map:str = ""
    game_state:bytes = b""
    positions = []


    @staticmethod
    def calculate_bullet_position(player_data:dict, distance:int) -> Tuple[int,int]: # Calcs target pos from angle and dist
        radian_angle = math.radians(player_data["angle_cannon"]) # Convert deg to rad
        vlx = distance * - math.sin(radian_angle) # X offset calc
        vly = distance * - math.cos(radian_angle) # Y offset calc

        x = player_data["x"] + math.sin(radian_angle) * -30 # Start X offset from tank
        y = player_data["y"] + math.cos(radian_angle) * -30 # Start Y offset from tank

        x += vlx # Add distance X
        y += vly # Add distance Y

        return x, y


    @classmethod
    def check_collision_bullet(cls, player_data: dict, collision_radius: int) -> dict: # Raycasts bullet vs bricks
        bullet_start_pos = Collision.calculate_bullet_position(player_data, 0) # Start pos
        bullet_end_pos = Collision.calculate_bullet_position(player_data, 100) # End pos

        steps = 10
        for step in range(steps + 1): # Raycast loop
            t = step / steps # Interp factor
            bullet_pos = ( # Cur ray point
                bullet_start_pos[0] + t * (bullet_end_pos[0] - bullet_start_pos[0]),
                bullet_start_pos[1] + t * (bullet_end_pos[1] - bullet_start_pos[1])
            )

            for brick in cls.bricks:
                brick: Brick
                target_pos = brick.rect.center # Target center
                distance = math.sqrt((bullet_pos[0] - target_pos[0]) ** 2 +
                                     (bullet_pos[1] - target_pos[1]) ** 2) # Dist calc
                collided = distance <= collision_radius # Dist check
                if collided:
                    if isinstance(brick, Brick):
                        brick.kill()
                        return { # Return broken brick
                            "type":5,
                            "x": brick.rect.x,
                            "y": brick.rect.y,
                            "w": brick.rect.w,
                            "h": brick.rect.h,
                        }

        return {}


    @classmethod
    def check_collision_player(cls, player_data: dict, collision_radius: int) -> dict: # Raycasts bullet vs players
        bullet_start_pos = Collision.calculate_bullet_position(player_data, 0) # Start pos
        bullet_end_pos = Collision.calculate_bullet_position(player_data, 100) # End pos

        steps = 10
        for step in range(steps + 1): # Raycast loop
            t = step / steps # Interp factor
            bullet_pos = ( # Cur ray point
                bullet_start_pos[0] + t * (bullet_end_pos[0] - bullet_start_pos[0]),
                bullet_start_pos[1] + t * (bullet_end_pos[1] - bullet_start_pos[1])
            )

            for other_player in cls.players:
                if other_player.get("name") == player_data.get("name"):
                    continue

                target_pos = (other_player["x"], other_player["y"]) # Target coords
                distance = math.sqrt((bullet_pos[0] - target_pos[0]) ** 2 +
                                     (bullet_pos[1] - target_pos[1]) ** 2) # Dist calc
                collided = distance <= collision_radius # Dist check
                if collided:
                    other_player["damage_indicator"] += Player.DAMAGE # Apply damage

                    if other_player["damage_indicator"] >= Player.MAX_DAMAGE: # Death check
                        random_index = random.randint(0, len(cls.positions) - 1) # Rand spawn index
                        other_player["damage_indicator"] = 0 # Reset damage

                        other_player["x"] = cls.positions[random_index][0] # Respawn X
                        other_player["y"] = cls.positions[random_index][1] # Respawn Y

                    return { # Return hit player
                            "type":7,
                            "player": other_player,
                    }

        return {}

    @classmethod
    def load(cls,lvl_map_tmx:str, func_tile_pack: Callable): # Loads map and bricks
        _tile_map = pytmx.TiledMap(lvl_map_tmx)
        cls.lvl_map = pathlib.Path(lvl_map_tmx).name
        cls.size_screen = (_tile_map.width * _tile_map.tilewidth,
                           _tile_map.height * _tile_map.tileheight) # Map dims

        for tile_object in _tile_map.objects: # Parse map objects
            if tile_object.name == "player":
                cls.positions.append((int(tile_object.x),int(tile_object.y))) # Store spawn
            elif tile_object.name == "brick":
                brick = Brick(tile_object.x,tile_object.y,tile_object.width,tile_object.height)
                data_tile = func_tile_pack({ # Pack brick data
                    "x": brick.rect.x,
                    "y": brick.rect.y,
                    "h": brick.rect.h,
                    "w": brick.rect.w,
                    "type": 5
                })
                brick.data = data_tile
                cls.game_state += data_tile # Add to initial map state
                cls.bricks.add(brick) # Add to group

    @classmethod
    def add_player(cls, player:dict): # Registers a player
        cls.players.append(player)

    @classmethod
    def collide_with_objects(cls, player: dict): # Resolves tank AABB collision vs walls
        body = pg.Rect(player["x"], player["y"], Player.SIZE_BODY_RECT[0], Player.SIZE_BODY_RECT[1]) # Tank rect
    
        for brock in cls.bricks:
            if not brock.alive():
                continue
                
            if not body.colliderect(brock.rect):
                continue
        
        for brock in list(cls.bricks):
            if not body.colliderect(brock.rect):
                continue
            overlap_left = brock.rect.right - body.left # Left intersect
            overlap_right = body.right - brock.rect.left # Right intersect
            overlap_top = brock.rect.bottom - body.top # Top intersect
            overlap_bottom = body.bottom - brock.rect.top # Bottom intersect

            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom) # Shallowest penetration
            
            if min_overlap == overlap_left: # Snap left
                player["x"] = brock.rect.right
            elif min_overlap == overlap_right: # Snap right
                player["x"] = brock.rect.left - body.width
            elif min_overlap == overlap_top: # Snap top
                player["y"] = brock.rect.bottom
            elif min_overlap == overlap_bottom: # Snap bottom
                player["y"] = brock.rect.top - body.height

            body.x = player["x"] # Update rect X
            body.y = player["y"] # Update rect Y

    @classmethod
    def check_bullet_at_point(cls, x: float, y: float): #Checks if the bullet has collided with the brick
        for brick in list(cls.bricks):
            if brick.rect.collidepoint(x, y):
                from battle_tanks.commons.package import Struct 
                return Struct.pack_tile({ #Returns the packet for the bullet
                    "type": Struct.BROKE_BRICK,
                    "x": brick.rect.x,
                    "y": brick.rect.y,
                    "w": brick.rect.w,
                    "h": brick.rect.h
                })
        return None

    @classmethod
    def get_laser_intersections(cls, player_data: dict, laser_range: int): # Raycasts laser vs players and bricks
        start_pos = cls.calculate_bullet_position(player_data, 0) # Ray start
        end_pos = cls.calculate_bullet_position(player_data, laser_range) # Ray end
        
        hit_objects = {"players": [], "bricks": []}
        steps = 20 # Step count
        
        for step in range(steps + 1):
            t = step / steps # Interp factor
            point = ( # Ray point
                start_pos[0] + t * (end_pos[0] - start_pos[0]),
                start_pos[1] + t * (end_pos[1] - start_pos[1])
            )

            for brick in cls.bricks:
                if brick.rect.collidepoint(point): # Brick hit check
                    if brick not in hit_objects["bricks"]:
                        hit_objects["bricks"].append(brick)

            for other_player in cls.players:
                if other_player.get("name") == player_data.get("name"):
                    continue
                p_rect = pg.Rect(other_player["x"], other_player["y"], 32, 32) # Player bounds
                if p_rect.collidepoint(point): # Player hit check
                    if other_player not in hit_objects["players"]:
                        hit_objects["players"].append(other_player)
        
        return hit_objects
