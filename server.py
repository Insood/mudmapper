import asyncio
import getopt
import re
import socket
import sys
from enum import Enum

MAP_HEIGHT = 20
MAP_WIDTH = 20

class Room:
    def __init__(self,name,x,y):
        self.name = name
        self.visisted = False
        self.exits = []
        self.x = x
        self.y = y

    def create_unvisited_exit(self,name, destination_room):
        e = Exit(self, destination_room, name)
        self.exits.append(e)
        return e

class Exit:
    def __init__(self, src_room, dest_room, name):
        self.name = name
        self.src_room = src_room
        self.dest_room = dest_room
        self.used = False

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

    def add(self, x,y, value):
        i = self.offset(x,y)
        if self.elements[i]:
            self.elements[i].append(value)
        else:
            self.elements[i] = [value]

    def count(self):
        counter = 0
        for room in self.elements:
            if room:
                counter += 1
        return counter

class Map:
    def __init__(self):
        self.rooms = []
        self.exits = []
        self.current_room = None
        self.matrix = Matrix(MAP_WIDTH,MAP_HEIGHT)

    def create_room(self,room_name, x,y):
        r = Room(room_name,x,y)
        self.matrix.set(x,y,r)
        return r

    def process_exits(self, room, exits):
        exits_copy = exits.copy()
        defined_exits = { "west": [-1,0],
                          "northwest": [-1,1],
                          "north": [0,-1],
                          "northeast": [1,-1],
                          "east":[1,0],
                          "southeast": [1,1],
                          "south": [0,1],
                          "southwest": [-1,1]}

        unprocessed_exits = []
        while exits_copy.length > 0:
            exit = exits_copy.pop()
            if exit in defined_exits:
                x_offset, y_offset = defined_exits[exit]
                new_room = self.create_room("Unknown", room.x + x_offset, room.y + y_offset)
                room.create_unvisited_exit(exit, new_room)
            else:
                unprocessed_exits.append(exit)

    def initial_room(self, room_name, exits):
        x = MAP_WIDTH/2
        y = MAP_HEIGHT/2
        self.create_room(room_name, x,y)

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

class TestMode:
    def __init__(self):
        pass

    def start(self):
        pass

if __name__=="__main__":
    if len(sys.argv) == 2:
        opt = sys.argv[1]
    else:
        opt = None
        
    if opt == "s":
        m = MapServer("localhost","9999")
        m.start()
    elif opt == "t":
        t = TestMode()
        t.start()
    else:
        print("Invalid command line option")
        print("%s s - Start the mapping server"%sys.argv[0])
        print("%s t - Start test mode"%sys.argv[0])