import asyncio
import map
import re
import socket
import sys

MAP_HEIGHT = 20
MAP_WIDTH = 20

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
        self.map = map.Map(MAP_WIDTH, MAP_HEIGHT)

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