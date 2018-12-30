import asyncio
import socket
import re
from enum import Enum

class RoomStatus(Enum):
    VISITED = 1
    UNVISITED = 2

class Room:
    def __init__(self,name,x,y, visisted):
        self.name = name
        self.x = x
        self.y = y
        self.visisted = visisted
        self.exits = []

    def __eq__(self,other):
        pass

class Exit:
    def __init__(self, src_room, dest_room, name):
        self.name = name
        self.src_room = src_room
        self.dest_room = dest_room

class Matrix:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.elements = [None]*(width*height)

    def offset(self,x,y):
        return y*self.width + x

    # (0,0) is at the top left corner!
    def get(self,x,y):
        i = self.offset(x,y)
        return self.elements[i]

    def set(self, x,y, value):
        i = self.offset(x,y)
        self.elements[i] = value

class Map:
    def __init__(self):
        self.rooms = []
        self.exits = []
        self.current_room = None

    def add_room(self, room_name, exits_array):
        r = Room()

    def find_room(self, room_name, exits_array):
        candidates = list(filter(lambda room: room.name == room_name, self.rooms))
        if len(candidates) == 0:
            return None
        

class DataHandler(asyncio.Protocol):
    def __init__(self,map):
        self.exits_regex = re.compile("(.*) \[exits: (.*),*\]")
        self.transport = None
        self.ignore_next_room = False
        self.last_command = None
        self.map = map

    def connection_made(self,transport):
        print("New Connection")
        self.transport = transport

    def data_received(self,data):
        lines = data.decode("ascii").split("\n")
        for line in lines:
            self.handle_line(line)

    def handle_line(self, line):
        prefix = line[0:2]
        data = line[2:]
        if prefix == "I:":
            self.detect_exits(data)
        if prefix == "O:":
            self.parse_command(data)

    # Some directions come pre-aliased in the MUD
    def expand_direction(self,cmd):
        directions = {"d":"down", "u":"up",
                      "n":"north", "e":"east", "w":"west","s":"south",
                      "nw":"northwest","sw":"southwest",
                      "ne":"northeast","se":"southeast"}
        if cmd in directions:
            return directions[cmd]
        else:
            return cmd

    def parse_command(self,line):
        line = line.strip()
        line = self.expand_direction(line)
        if line in ["l","look"]:
            self.ignore_next_room = True

        self.last_command = line

    def detect_exits(self,line):
        matches = re.match(self.exits_regex, line)
        if matches:
            # Silently consume the room sdesc that was received due to the player having typed 'look' (or similar)
            if self.ignore_next_room:
                self.ignore_next_room = False
                return

            room_name = matches.group(1)
            exit_string  = matches.group(2)
            exits = [ exit_name.strip() for exit_name in exit_string.split(",")]
            self.on_enter_room(room_name, exits)
            
    def on_enter_room(self, room_name, exits):
        print("Last Command: [%s] Room: [%s], Exits: %s"%(self.last_command, room_name, exits))

class MapServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.map = Map()

    def start(self):
        loop = asyncio.get_event_loop()
        coro = loop.create_server(lambda: DataHandler(self.map), self.host,  self.port)

        server = loop.run_until_complete(coro)
        
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()

if __name__=="__main__":
    m = MapServer("localhost","9999")
    m.start()