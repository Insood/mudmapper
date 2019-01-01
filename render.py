import pygame
import random
import map

WHITE = (255,255,255)
BLUE =  (0,   0, 255)
GRID_SIZE  = 30 # pixels per one room coordinate
MAP_WIDTH  = 20
MAP_HEIGHT = 20
ROOM_SIZE  = 24
BORDER     = (GRID_SIZE-ROOM_SIZE)/2
VISITED_ROOM_BORDER = 3
UNVISITED_ROOM_BORDER = 1

class Display:
    def __init__(self, map):
        pygame.init()
        pygame.display.set_caption("Mapper")
        self.map = map
        self.width = GRID_SIZE * MAP_WIDTH
        self.height = GRID_SIZE * MAP_HEIGHT
        self.screen = pygame.display.set_mode((self.width,self.height))
        self.clock = pygame.time.Clock()
        self.selected_room = None

    def draw_room(self, room):
        rect = self.room_rect(room)
        if room.visited:
            border = VISITED_ROOM_BORDER
        else:
            border = UNVISITED_ROOM_BORDER

        pygame.draw.rect(self.screen,BLUE, rect, border)

    def draw_exits(self, room):
        for exit in room.exits:
            start = self.room_center_screen_coordinates(exit.src_room)
            end   = self.room_center_screen_coordinates(exit.dest_room)
            pygame.draw.line(self.screen, BLUE, start,end,5)

    def draw(self):
        self.screen.fill(WHITE)
        room_matrix = self.map.matrix
    
        for x in range(0, room_matrix.width):
            for y in range(0, room_matrix.height):
                rooms = room_matrix.get(x,y)
                if rooms:
                    for room in rooms:
                        self.draw_room(room)
                        self.draw_exits(room)
        pygame.display.flip()

    def room_center_screen_coordinates(self,room):
        x, y = self.transform_to_screen_coordinates(room.x, room.y)
        return int(x + GRID_SIZE/2), (y+GRID_SIZE/2)
        
    def room_rect(self, room):
        x, y = self.transform_to_screen_coordinates(room.x, room.y)
        x = x + BORDER
        y = y + BORDER
        return [x,y, ROOM_SIZE, ROOM_SIZE]

    def transform_to_screen_coordinates(self,x,y):
        left = int(x*GRID_SIZE + BORDER)
        top = int(y*GRID_SIZE + BORDER)
        return left, top

    def screen_coordinates_to_map(self, screen_x, screen_y):
        x = int(screen_x/GRID_SIZE)
        y = int(screen_y/GRID_SIZE)
        return x,y

    def on_click(self):
        scr_x, scr_y = pygame.mouse.get_pos()
        x, y = self.screen_coordinates_to_map(scr_x, scr_y)
        rooms = self.map.matrix.get(x,y)
        if rooms:
            self.selected_room = rooms[0]

    def on_keydown(self,key):
        if key == pygame.K_ESCAPE:
            self.running = False

        if not self.selected_room:
            return
        
        if key == pygame.K_LEFT:
            self.map.relocate_room(self.selected_room, self.selected_room.x - 1, self.selected_room.y)
        elif key == pygame.K_UP:
            self.map.relocate_room(self.selected_room, self.selected_room.x , self.selected_room.y-1)
        elif key == pygame.K_RIGHT:
            self.map.relocate_room(self.selected_room, self.selected_room.x + 1, self.selected_room.y)
        elif key == pygame.K_DOWN:
            self.map.relocate_room(self.selected_room, self.selected_room.x, self.selected_room.y+1)

    def start(self):
        self.running = True
        while self.running:
            self.clock.tick(10)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.on_click()
                elif event.type == pygame.KEYDOWN:
                    self.on_keydown(event.key)
            self.draw()

def build_map():
    m = map.Map(MAP_WIDTH, MAP_HEIGHT)
    raw   = ["north;Northern part of Elsendor;east;north;south;west",
             "north;Northern edge of Elsendor;ct;east;south;west",
             "east;A road in the northeastern part of Elsendor;east;south;west",
             "east;Northeast corner of Elsendor;east;north;south;west",
             "south;Eastern part of Elsendor;east;north;south;west",
             "south;The east edge of Elsendor;north;som;south;west",
             "west;Eastern part of the main road;east;north;south;west",
             "west;The center of Elsendor;down;east;newbie;north;south;west",
             "west;Western part of the main road;east;north;south;west",
             "west;The western part of Elsendor;east;ff6;north;south",
             "north;Western part of Elsendor;north;south;west",
             "north;Northwest corner of Elsendor;east;north;south;west",
             "north;Elsendor's Ninja Shop;east;south"]
    rooms = []
    for r in raw:
        parts = r.split(";")
        direction = parts[0]
        room_name = parts[1]
        exits = parts[2:]
        rooms.append({"direction": direction, "name": room_name, "exits": exits})

    r1 = rooms[0]
    m.initial_room(r1["name"], r1["exits"])

    for room in rooms[1:]:
        m.move(room["direction"], room["name"], room["exits"])
    return m

if __name__=="__main__":
    m = build_map()
    d = Display(m)
    d.start()