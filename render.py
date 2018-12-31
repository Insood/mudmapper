import pygame
import random

WIDTH = 800
HEIGHT = 600
WHITE = (255,255,255)
BLUE =  (0,   0, 255)
GRID_SIZE = 20 # 20 pixels per one room coordinate
ROOM_SIZE = 15

class Room:
    def __init__(self,x,y):
        self.x = x
        self.y = y

class Application:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Mapper") 
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT))
        self.clock = pygame.time.Clock()
        self.rooms = []
        self.generate_rooms()

    def generate_rooms(self):
        rooms = []
        for i in range(100):
            x = random.randint(-10,10)
            y = random.randint(-10,10)
            r = Room(x,y)
            rooms.append(r)

        self.rooms = rooms

    def draw(self):
        self.screen.fill(WHITE)
        for room in self.rooms:
            rect = self.transform_to_screen_coordinates(room.x, room.y, ROOM_SIZE, ROOM_SIZE)
            pygame.draw.rect(self.screen,BLUE, rect, 2)
        pygame.display.flip()

    def transform_to_screen_coordinates(self,x,y,w,h):
        left = int(WIDTH/2 + x*GRID_SIZE - w/2)
        top = int(HEIGHT/2 + y*GRID_SIZE - w/2)
        return [left, top, w, h]

    def start(self):
        self.running = True
        while self.running:
            self.clock.tick(10)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.draw()

        
if __name__=="__main__":
    app = Application()
    app.start()