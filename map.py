from enum import Enum

class Room:
    def __init__(self,name,x,y):
        self.name = name
        self.visited = False
        self.exits = []
        self.x = x
        self.y = y

    def create_exit(self,name, destination_room):
        e = Exit(self, destination_room, name)
        self.exits.append(e)
        return e

    def get_exit_by_name(self,exit_name):
        for exit in self.exits:
            if exit.name == exit_name:
                return exit

        return None

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

    def remove(self, x,y, value):
        i = self.offset(x,y)
        if self.elements[i]:
            print(self.elements[i])
            self.elements[i] = list(filter(lambda list_item: list_item is not value , self.elements[i]))
            print(self.elements[i])

    def count(self):
        counter = 0
        for room in self.elements:
            if room:
                counter += 1
        return counter

class Map:
    def __init__(self, width, height):
        self.rooms = []
        self.exits = []
        self.current_room = None
        self.matrix = Matrix(width, height)

    def create_room(self,room_name, x,y):
        r = Room(room_name,x,y)
        self.matrix.add(x,y,r)
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
        while len(exits_copy) > 0:
            exit = exits_copy.pop()
            if exit in defined_exits:
                x_offset, y_offset = defined_exits[exit]
                new_room = self.create_room("Unknown", room.x + x_offset, room.y + y_offset)
                room.create_exit(exit, new_room)
            else:
                unprocessed_exits.append(exit)

    def initial_room(self, room_name, exits):
        x = int(self.matrix.width/2)
        y = int(self.matrix.height/2)
        room = self.create_room(room_name, x,y)
        room.visited = True
        self.process_exits(room, exits)
        self.current_room = room

    def relocate_room(self, room, new_x, new_y):
        self.matrix.remove(room.x, room.y, room)
        room.x = new_x
        room.y = new_y
        self.matrix.add(room.x, room.y, room)


    def move(self, exit_taken, new_room_name, room_exits):
        exit = self.current_room.get_exit_by_name(exit_taken)
        if exit:
            exit.used = True # Even if it was True before
            if exit.dest_room.visited:
                if exit.dest_room.name != new_room_name:
                    raise RuntimeError("Expected to go to %s, but actually went to %s"%(exit.dest_room.name, new_room_name))
            else:
                exit.dest_room.visited = True
                self.process_exits(exit.dest_room, room_exits)

            self.current_room = exit.dest_room
        else:
            raise NotImplementedError
            #self.current_room.create_exit(exit_name, ...)
            