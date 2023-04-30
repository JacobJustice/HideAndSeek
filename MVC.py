import pygame
import sys
import random
from player import Player
from SimpleAI import SimpleAI
from Obstacle import Obstacle

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
NUM_OBSTACLES = 10

def get_ai_spawn_location(edge):
    #edge 0: x= 0, screenwidth ; y = 0
    if edge == 0:
        return (random.randint(0, SCREEN_WIDTH), 0)
    #edge 1: x= 0, screenwidth ; y = screenheight
    elif edge == 1:
        return (random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT)
    #edge 2: x= screenwidth ; y = 0, screenheight
    elif edge == 2:
        return (SCREEN_WIDTH, random.randint(0, SCREEN_HEIGHT))
    #edge 3: x= 0 ; y = 0, screenheight
    elif edge == 3:
        return (0, random.randint(0, SCREEN_HEIGHT))
    else:
        return (0,0)

class Model:
    screen_width = SCREEN_WIDTH
    screen_height = SCREEN_HEIGHT
    FPS = 60
    running = True
    clock = pygame.time.Clock()
    score = [0,0]
    passed_time = 0.0
    ai_spawn_times = set()

    def generate_AI(self):
        edge = random.randint(0,3)
        xy = get_ai_spawn_location(edge)

        self.entities.append(SimpleAI(
                 x=xy[0]
                ,y=xy[1]
                ,radius=random.randrange(10,25)
                ,color=(0,50,200)
                ,speed=random.randrange(2,5)
                ))

    def __init__(self):
        self.player = Player(x=100,y=100,radius=10,color=(255,0,0), speed=5)
        self.entities = [self.player]
        self.obstacles = [Obstacle(SCREEN_WIDTH, SCREEN_HEIGHT) for x in range(NUM_OBSTACLES)]
        self.generate_AI()

    def __str__(self):
        return ''
    
    def update(self, controller):
        if controller.quit:
            pygame.quit()
            sys.exit()

        #calculate dt
        dt = self.clock.tick(self.FPS) / 1000
        self.passed_time += dt

        if int(self.passed_time) not in self.ai_spawn_times and self.passed_time % 10 < 1:
            print("SPAWNING AI")
            self.generate_AI()
            self.ai_spawn_times.add(int(self.passed_time))

        #update entities
        self.player.update(self.obstacles, controller)

        #skip first entity for update, because that's the player
        for ai in self.entities[1:]:
            if ai.update(self.obstacles, self.player) == 1:
                print("YOU LOSE!!")
                pygame.quit()
                sys.exit()


class View:
    screen = None
    background_color = (64, 64, 64)
    def __init__(self, screen):
        self.screen = screen

    def display(self, model):
        self.screen.fill(self.background_color)
        for entity in model.entities:
            entity.display(self.screen)
        for obstacle in model.obstacles:
            obstacle.display(self.screen)
        pygame.display.update()


# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_RIGHT,
    K_LEFT,
    K_w,
    K_a,
    K_s,
    K_d,
    KEYDOWN,
    QUIT,
)

class Controller:
    quit = False
    player_left = False
    player_right = False
    player_up = False
    player_down = False
    
    def update(self):
        self.player_down = False
        self.player_up = False
        self.player_left = False
        self.player_right = False        
        for event in pygame.event.get():
            if event.type == QUIT:
                self.quit = True

        keys = pygame.key.get_pressed()
        if keys[K_UP] or keys[K_w]:
            self.player_up = True
        if keys[K_DOWN] or keys[K_s]:
            self.player_down = True
        if keys[K_RIGHT] or keys[K_d]:
            self.player_right = True
        if keys[K_LEFT] or keys[K_a]:
            self.player_left = True
                
if __name__ == '__main__':
    import main