from typing import Union, Dict, List
import pickle
import struct
import math

from battle_tanks.components.collision import Collision
from battle_tanks.sprites.player import Player


BUFFER_SIZE_INIT_PLAYER = 4
BUFFER_SIZE_EVENT = 1
BUFFER_SIZE_NAME = 32


class Struct:
    """
        Class for packing and unpacking data
    """
    SIZE_PLAYER = 12 + 1 # ADD 1 FOR SIZE (updated to include tank_color)
    MAX_PLAYERS = 2
    BUFFER_SIZE_PLAYER = 100
    BUFFER_SIZE_EVENT_RESPONSE = 11 # ADD 1 FOR SIZE
    BUFFER_SPLIT_MAP = BUFFER_SIZE_EVENT_RESPONSE * 8
    BUFFER_SIZE_LVL_MAP = 40 # Buffer size for level map name
    BUFFER_SIZE_NAME = 32 # Buffer size for player name
    BUFFER_SIZE_EVENT = 1 # Buffer size for an event byte

    OK_MESSAGE = b'\x01' # OK message
    JOIN_MESSAGE = b'\x02' # Player joined
    USER_NOT_AVAILABLE = b'\x09' # Username taken
    CLOSE_CONN = b'\x10' # Closing connection

    LEFT_EVENT_PLAYER: bytes = b'\x03' # Moving left
    RIGHT_EVENT_PLAYER: bytes = b'\x04' # Moving right
    UP_EVENT_PLAYER: bytes = b'\x05' # Moving up
    DOWN_EVENT_PLAYER: bytes = b'\x06' # Moving down
    SHOOT_EVENT_PLAYER: bytes = b'\x06' # Shooting (duplicate of down, possibly unused or buggy)

    """ LEFT TOWERS """
    LEFT_ANGLE_EVENT_PLAYER: bytes = b'\x07' # Rotating turret left
    RIGHT_ANGLE_EVENT_PLAYER: bytes = b'\x08' # Byte code for rotating turret right

    """ FIRE EVENTS"""
    FIRE_EVENT_PLAYER: bytes = b'\x11' # Byte code for firing bullet

    LASER_ON_EVENT = b"\x12" # Byte code for turning laser on
    LASER_OFF_EVENT = b"\x13" # Byte code for turning laser off

    UPDATE_PLAYER: int = 1 # Status code for updating an existing player
    NEW_PLAYER: int = 2 # Status code for a new player joining
    OLD_PLAYER: int = 3 # Status code for an existing player


    BROKE_BRICK:int = 4 # Status code indicating a brick was broken
    BRICK:int = 5 # Status code for a brick tile
    BLOCK:int = 6 # Status code for an indestructible block
    PLAYER_SHOT:int = 7 # Status code indicating a player was shot

    STATUS_PLAYER = [UPDATE_PLAYER, NEW_PLAYER, OLD_PLAYER, PLAYER_SHOT] #Valid player status codes

    MOVES = [ #Valid movement byte codes
            LEFT_EVENT_PLAYER,
            RIGHT_EVENT_PLAYER,
            UP_EVENT_PLAYER,
            DOWN_EVENT_PLAYER,

            #TOWERS MOVES
            LEFT_ANGLE_EVENT_PLAYER,
            RIGHT_ANGLE_EVENT_PLAYER,

             ]

    @staticmethod #Used to unpack player or event data
    def unpack_single_data(data: bytes) -> tuple: # Unpacks a single byte into a tuple
        """ :param data: bytes"""
        return struct.unpack('B', data)

    @staticmethod #Used to pack player or event data
    def pack_single_data(data) -> bytes: # Packs a single value into a byte
        """ :param data: example: 1"""
        return struct.pack('B', data)       

    @staticmethod #Used to unpack player data
    def unpack_player(data: bytes): # Unpacks 11 bytes(+ 1 size byte) of player data into a tuple after stripping the size byte
        data = data[1:]
        return struct.unpack('BBhhhhbB', data) #
    @staticmethod
    def pack_player(data: Union[bytes, None],
                    player_data: dict,
                    status=None) -> bytes: # Applies physics if move event, then packs player state (status, position, x, y, angle, cannon angle, damage, color) into 13 bytes

        angle = player_data["angle"] #Gets the angle of the player
        angle_cannon = player_data["angle_cannon"] #Gets the angle of the cannon
        radians = math.radians(angle) #Converts the angle to radians
        damage_indicator = player_data["damage_indicator"] #Gets the damage indicator

        if data in Struct.MOVES: # Checks if data is a valid move
            if data == Struct.RIGHT_EVENT_PLAYER:
                angle += Player.ANGLE * Player.ANGLE_RIGHT
                angle_cannon += Player.ANGLE * Player.ANGLE_RIGHT
            elif data == Struct.LEFT_EVENT_PLAYER:
                angle -= Player.ANGLE * Player.ANGLE_RIGHT
                angle_cannon += Player.ANGLE * Player.ANGLE_LEFT
            elif data == Struct.LEFT_ANGLE_EVENT_PLAYER:
                angle_cannon += Player.ANGLE * Player.ANGLE_LEFT
            elif data == Struct.RIGHT_ANGLE_EVENT_PLAYER:
                angle_cannon += Player.ANGLE * Player.ANGLE_RIGHT

            if (data == Struct.UP_EVENT_PLAYER or data == Struct.DOWN_EVENT_PLAYER): #Checks if data is up or down
                vlx = Player.SPEED * - math.sin(radians)
                vly = Player.SPEED * - math.cos(radians)

                if data == Struct.UP_EVENT_PLAYER:
                    player_data["y"] += vly
                    player_data["x"] += vlx
                    
                elif data == Struct.DOWN_EVENT_PLAYER:
                    player_data["y"] -= vly
                    player_data["x"] -= vlx

                Collision.collide_with_objects(player_data) #Checks for collisions

        current = player_data["position"] #Gets the position
        pos_x = player_data["x"] #Gets the x position
        pos_y = player_data["y"] #Gets the y position
        angle = angle % 360 #Converts angle to be within 0-360
        angle_cannon = angle_cannon % 360 #Converts cannon angle to be within 0-360
        tank_color = player_data.get("tank_color", 0) #Gets the tank color

        player_data["angle"] = angle
        player_data["angle_cannon"] = angle_cannon

        size_data = Struct.pack_single_data(Struct.SIZE_PLAYER)
        size_data += struct.pack('BBhhhhbB', status if status is not None else Struct.UPDATE_PLAYER,
                           current, int(pos_x), int(pos_y), int(angle), int(angle_cannon), int(damage_indicator), int(tank_color))

        return size_data


    @staticmethod
    def unpack_all_data(data: bytes) -> list: # Splits a raw byte buffer into individual player or event packets based on size prefix
        index = 0
        step = 0
        data_wrapped:List[tuple] = []

        while index < len(data):
            # Check for player-sized packets (which now includes your bullets)
            if data[index] == Struct.SIZE_PLAYER:
                step += Struct.SIZE_PLAYER
                chunk = data[index :step]

                if len(chunk) == Struct.SIZE_PLAYER:
                    # Unpack the chunk (status is the first byte after size)
                    unpacked = Struct.unpack_player(chunk)
                    data_wrapped.append(unpacked)
                index = step

            # Check for event-sized packets (like bricks breaking)
            elif data[index] == Struct.BUFFER_SIZE_EVENT_RESPONSE:
                step += Struct.BUFFER_SIZE_EVENT_RESPONSE
                chunk = data[index:step]

                if len(chunk) == Struct.BUFFER_SIZE_EVENT_RESPONSE:
                    data_wrapped.append(Struct.unpack_event(chunk))

                index = step
            else:
                index += 1 # Advance to prevent infinite loops if data is corrupted

        return data_wrapped


    @staticmethod
    def unpack_players(data: bytes) -> list: # Decodes a sequence of player data chunks into a list of player tuples
        players = []
        chunk_size = Struct.BUFFER_SIZE_PLAYER

        # Check if data length is greater than 14
        if len(data) > chunk_size:
            for i in range(0, len(data), chunk_size):
                chunk = data[i+1:i + chunk_size]
                player = Struct.unpack_player(chunk)
                players.append(player)
        else:
            if len(data) > 0:
                player = Struct.unpack_player(data)
                players.append(player)

        return players


    @staticmethod
    def pack_players(data: Dict[int, dict], status = None) -> bytes: # Packs all players in the dictionary into a concatenated byte buffer
        data_encoded = [ Struct.pack_player(None, item, status) for d, item in data.items()]
        return b"".join(map(bytes,data_encoded))

    @staticmethod
    def pack_tile(data: dict): # Packs a tile event (type, x, y, w, h) into an 11-byte packet
        data_size = Struct.pack_single_data(Struct.BUFFER_SIZE_EVENT_RESPONSE)
        data_size += struct.pack("bhhhh", int(data["type"]), int(data["x"]),
                           int(data["y"]), int(data["w"]), int(data["h"]))

        return data_size

    @staticmethod
    def pack_event(player_data: dict) -> Union[bytes, bool]: # Checks for player and bullet collisions, returning a packed event or False
        player_collided = Collision.check_collision_player(player_data,collision_radius=30)

        if player_collided.get("player") is not None:
            return Struct.pack_player(None, player_collided.get("player"), player_collided.get("type"))

        data_collided = Collision.check_collision_bullet(player_data, 30)
        if len(data_collided.items()) > 0:
            if data_collided["type"] == Struct.BRICK:
                data_collided["type"] = Struct.BROKE_BRICK
            return Struct.pack_tile(data_collided)

        return False


    @staticmethod
    def unpack_event(data: bytes): # Unpacks an 11-byte tile/event packet into a tuple after stripping the size byte
        data = data[1:]
        return struct.unpack('bhhhh', data)


    @staticmethod
    def unpack_events(data: bytes) -> list: # Decodes a sequence of event chunks into a list of event tuples
        """ Decode data in chunks of 14 bytes if data length is greater than 14. """
        events = []
        chunk_size = Struct.BUFFER_SIZE_EVENT_RESPONSE

        # Check if data length is greater than 14
        if len(data) > chunk_size:
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                _event = Struct.unpack_event(chunk)
                events.append(_event)
        else:
            if len(data) > 0:
                _event = Struct.unpack_event(data)
                events.append(_event)

        return events


    @staticmethod
    def pack(data: Union[str, dict]): # Serializes data using pickle or utf-8 encoding
        """:param data: str or object.  encode data. deprecate. """
        try:
            return pickle.dumps(data)
        except pickle.PicklingError as e:
            return data.encode('utf-8')


    @staticmethod
    def unpack(data: bytes): # Deserializes data using pickle or utf-8 decoding
        """ decode data """
        try:
            return pickle.loads(data)
        except pickle.UnpicklingError as e:
            return data.decode('utf-8')

    # Add a new status for moving bullets
    BULLET_MOVE: int = 8 
    
    @staticmethod
    def pack_bullet_position(bullet_id, x, y): # Packs a bullet position update into a byte buffer for server-side simulation
        # Pack status, unique ID, and coordinates
        size_data = Struct.pack_single_data(Struct.SIZE_PLAYER)
        # Using a similar format to UPDATE_PLAYER but for a bullet
        size_data += struct.pack('BBhhhhb', Struct.BULLET_MOVE, bullet_id, int(x), int(y), 0, 0, 0)
        return size_data
    
