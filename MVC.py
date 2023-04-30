import pygame
import numpy as np
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
        self.lost = False
        self.clock = pygame.time.Clock()
        self.passed_time = 0.0
        self.ai_spawn_times = set()
        obs_size = 50
        self.player = Player(x=SCREEN_WIDTH/2,y=SCREEN_HEIGHT/2,radius=10,color=(255,0,0), speed=5)
        self.obstacles = [Obstacle(SCREEN_WIDTH, SCREEN_HEIGHT, size=obs_size) for x in range(NUM_OBSTACLES)]
        # ensure player isn't colliding with obstacles
        center = np.array((self.player.x, self.player.y))
        for i, obstacle in enumerate(self.obstacles):
            inside = obstacle.is_circle_inside_polygon(center, self.player.radius) or obstacle.collision(center, self.player)
            while inside:
                self.obstacles[i] = Obstacle(SCREEN_WIDTH, SCREEN_HEIGHT,size=obs_size)
                print(self.obstacles[i].size)
                inside = self.obstacles[i].is_circle_inside_polygon(center, self.player.radius) or self.obstacles[i].collision(center, self.player)[0]
                print(inside)
        self.entities = [self.player]
        self.generate_AI()

    def __str__(self):
        return ''
    
    def update(self, controller):
        if controller.quit:
            pygame.quit()
            sys.exit()
        if self.lost and controller.space:
            self.lost = False
            self.__init__()

        #calculate dt
        dt = self.clock.tick(self.FPS) / 1000
        self.passed_time += dt

        if int(self.passed_time) not in self.ai_spawn_times and self.passed_time % 10 < 1:
            print("SPAWNING AI")
            self.generate_AI()
            self.ai_spawn_times.add(int(self.passed_time))

        #update entities
        if not self.lost:
            self.player.update(self.obstacles, controller)

        #skip first entity for update, because that's the player
        for ai in self.entities[1:]:
            if ai.update(self.obstacles, self.player) == 1:
                # you lose the game
                self.lost = True


class View:
    screen = None
    background_color = (64, 64, 64)
    font_color = (255,255,255)
    def __init__(self, screen):
        self.screen = screen
        self.start_time = pygame.time.get_ticks()
        self.font = pygame.font.SysFont("Arial", 32)
        self.elapsed_time = pygame.time.get_ticks() - self.start_time
        self.lose_font = pygame.font.SysFont("Arial", 64)
        self.lose_text1 = self.lose_font.render("YOU LOSE!!", True, self.font_color)
        self.lose_text1rect = self.lose_text1.get_rect(center = (SCREEN_WIDTH/2, (SCREEN_HEIGHT/2) - 65))
        self.lose_text2 = self.lose_font.render("Press space to try again", True, self.font_color)
        self.lose_text2rect = self.lose_text2.get_rect(center = (SCREEN_WIDTH/2, (SCREEN_HEIGHT/2)))

    def display(self, model):
        self.screen.fill(self.background_color)
        for obstacle in model.obstacles:
            obstacle.display(self.screen)
        for entity in model.entities:
            entity.display(self.screen)
        if not model.lost:
            self.elapsed_time = pygame.time.get_ticks() - self.start_time
        else:
            self.screen.blit(self.lose_text1, self.lose_text1rect)
            self.screen.blit(self.lose_text2, self.lose_text2rect)
            
        timer = self.font.render(str(self.elapsed_time / 1000), True, self.font_color)
        ai_spawned = self.font.render("AI Spawned:" + str(len(model.entities)-1), True, self.font_color)
        self.screen.blit(ai_spawned, (150, 68))
        self.screen.blit(timer, (150, 100))
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
    K_SPACE,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

class Controller:
    quit = False
    player_left = False
    player_right = False
    player_up = False
    player_down = False
    space = False
    
    def update(self):
        self.player_down = False
        self.player_up = False
        self.player_left = False
        self.player_right = False        
        self.space = False
        for event in pygame.event.get():
            if event.type == QUIT:
                self.quit = True

        keys = pygame.key.get_pressed()
        if keys[K_ESCAPE]:
            self.quit = True
        if keys[K_UP] or keys[K_w]:
            self.player_up = True
        if keys[K_DOWN] or keys[K_s]:
            self.player_down = True
        if keys[K_RIGHT] or keys[K_d]:
            self.player_right = True
        if keys[K_LEFT] or keys[K_a]:
            self.player_left = True
        if keys[K_SPACE]:
            self.space = True
        
                
if __name__ == '__main__':
    import main