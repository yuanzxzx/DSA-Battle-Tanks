"""Server TCP connection"""

import socket
import struct
from typing import Tuple, List, Union
from battle_tanks.commons.package import Struct

from queue import SimpleQueue

class NetworkComponent:
    """ Client TCP connection """

    def __init__(self, addr: Tuple[str, int], name: str = "John", tank_color: int = 0): #Designates Tank Color for players      
        self.name = name
        self.addr = addr
        self.tank_color = tank_color
        self.lvl_map: str = ""
        
        # Instance-specific queues (not shared across instances)
        self.SEND_Q = SimpleQueue() #Sends Data from Client to Server
        self.UPDATE_Q = SimpleQueue() #Receives Data from Server to Client

        self._socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Creates TCP Socket
        self._socket_tcp.connect(addr) #Connects to Server
        self._socket_tcp.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1) #Disables Nagle's Algorithm

        self.game_state: bytes = b"" #Initializes Game State
        self._player_data: Union[dict, bytes] = self.load_data() #uipdates gahmestate


    def load_data(self) -> Union[dict, bytes]:
        """ Load player data INIT """
        ok = self._socket_tcp.recv(Struct.BUFFER_SIZE_EVENT)
        if ok == Struct.OK_MESSAGE:
            # Send name and tank_color
            # Pad name to fixed length so server knows where color byte is
            name_data = self.name.encode('utf-8')
            # Pad or truncate to BUFFER_SIZE_NAME
            if len(name_data) < Struct.BUFFER_SIZE_NAME: 
                name_data = name_data + b'\x00' * (Struct.BUFFER_SIZE_NAME - len(name_data))
            else:
                name_data = name_data[:Struct.BUFFER_SIZE_NAME]
            
            color_data = struct.pack('B', int(self.tank_color)) #PACKS COLOR DATA
            self._socket_tcp.send(name_data + color_data)
            lvl_map = self._socket_tcp.recv(Struct.BUFFER_SIZE_LVL_MAP)
            if lvl_map == Struct.USER_NOT_AVAILABLE: #CHECKING USER AVAILABILITY
                return Struct.USER_NOT_AVAILABLE

            self.lvl_map = Struct.unpack(lvl_map) #Unpacks Map

            data = self._socket_tcp.recv(Struct.SIZE_PLAYER) #Initializes Game State
            data_player = Struct.unpack_player(data)
            size_map = Struct.unpack_single_data(self._socket_tcp.recv(Struct.BUFFER_SIZE_EVENT)) #Receives Size of Map

            for i in range(size_map[0]): #Receives Size of Map
                split_map = self._socket_tcp.recv(Struct.BUFFER_SPLIT_MAP)
                self.game_state += split_map

            return { #Initializes Game State
                "position": data_player[1],
                "x": data_player[2],
                "y": data_player[3],
                "angle": data_player[4],
                "angle_cannon": data_player[5],
                "tank_color": data_player[7] if len(data_player) > 7 else 0
            }

    @staticmethod #Modifies Data
    def _modify_data(data_arr: list) -> dict:
        if data_arr[0] in Struct.STATUS_PLAYER: #Modifies Player Data
            return {
                "status": data_arr[0],
                "position": data_arr[1],
                "x": data_arr[2],
                "y": data_arr[3],
                "angle": data_arr[4],
                "angle_cannon": data_arr[5],
                "damage_indicator": data_arr[6],
                "tank_color": data_arr[7] if len(data_arr) > 7 else 0
            }

        elif data_arr[0] == Struct.BROKE_BRICK: #Modifies Brick Data
            return {
                "status": data_arr[0],
                "x": data_arr[1],
                "y": data_arr[2],
                "w": data_arr[3],
                "h": data_arr[4],
            }


    def recv_move_player(self) -> List[dict]: #Receives Game State
        try:
            data = self._socket_tcp.recv(120) #Receives Game State
            if data != b'': #Receives Game State
                data_set = Struct.unpack_all_data(data) #Receives Game State
                return list(map(NetworkComponent._modify_data, data_set)) #Receives Game State
        except BlockingIOError as e:
            # print(f"BLOCKING AS: {e}")
            pass
        except socket.error as e: #Handles Socket Errors
            print(f"THERE IS A ERROR: {e}")
            pass

        return []


    def send_move_tcp(self, move: bytes): #Sends Game State
        try:
            self._socket_tcp.send(move) #Sends Game State
        except socket.error as e: #Handles Socket Errors
            self._socket_tcp.close() #Closes Socket


    @property #Returns Player Data
    def player_data(self) -> Union[dict, bytes]:
        """ get number of player """
        return self._player_data


    @property
    def player_number(self) -> int:
        """ get number of player """
        if self._player_data == Struct.USER_NOT_AVAILABLE:
            return 0

        return self._player_data["position"]


    @property
    def socket_tcp(self) -> socket.socket: 
        return self._socket_tcp


    @staticmethod
    def check_name(addr: tuple, name: str) -> Union[bool, socket.error]: #Checks if Name is Available   
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            sock.connect(addr)

            if sock.recv(Struct.BUFFER_SIZE_EVENT) == Struct.OK_MESSAGE:
                # Send check request with fixed-length padded name
                check_name = (name + "-c").encode('utf-8')
                if len(check_name) < Struct.BUFFER_SIZE_NAME:
                    check_name = check_name + b'\x00' * (Struct.BUFFER_SIZE_NAME - len(check_name))
                else:
                    check_name = check_name[:Struct.BUFFER_SIZE_NAME]
                # Add a dummy color byte to match the 33-byte format
                check_name = check_name + struct.pack('B', 0)
                sock.send(check_name)
                return sock.recv(1) == Struct.OK_MESSAGE

        except socket.error as e:
            return e

        return False


    def get_events_to_game_state(self): #Gets Game State
        """
        Extracts and returns the events from the current game state.

        This method uses the Struct class to unpack events from the 
        game_state attribute of the instance.

        Returns:
            list: A list of events extracted from the game state.
        """
        return Struct.unpack_events(self.game_state)


    def send_keys(self, keys: List[bytes]) -> None: #Sends Game State
        for action in keys: #Sends Game State
            self.SEND_Q.put(action) #Sends Game State

    
    def recv_to_queue(self) -> bytes: #Receives Game State
        data = [] #Receives Game State
        while self.UPDATE_Q.empty() is False: #Receives Game State
            data.extend(self.UPDATE_Q.get()) #Receives Game State
    
        return data