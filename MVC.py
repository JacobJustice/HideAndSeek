import pygame
import numpy as np
import sys
import random
from player import Player
from SimpleAI import SimpleAI
from RRTAI import RRTAI
from RandomAI import RandomAI
from Obstacle import Obstacle, check_collision

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
MIN_RADIUS = 10
MAX_RADIUS = 25
NUM_OBSTACLES = 15

def get_ai_spawn_location(edge, obstacles):
    #edge 0: x= 0, screenwidth ; y = 0
    if edge == 0:
        spawn = (random.randint(0, SCREEN_WIDTH), 0)
    #edge 1: x= 0, screenwidth ; y = screenheight
    elif edge == 1:
        spawn = (random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT)
    #edge 2: x= screenwidth ; y = 0, screenheight
    elif edge == 2:
        spawn = (SCREEN_WIDTH, random.randint(0, SCREEN_HEIGHT))
    #edge 3: x= 0 ; y = 0, screenheight
    else:
        spawn = (0, random.randint(0, SCREEN_HEIGHT))
    if not check_collision(spawn, 20, obstacles):
        return spawn
    else:
        return get_ai_spawn_location(random.randint(0,3), obstacles)

class Model:
    screen_width = SCREEN_WIDTH
    screen_height = SCREEN_HEIGHT
    FPS = 60
    running = True
    debug = True
    loadingfont = None
    def __init__(self, gen_obstacles=True):
        self.lost = False
        self.clock = pygame.time.Clock()
        self.passed_time = 0.0
        self.ai_spawn_times = set()
        obs_size = 35

        # gen player and obstacles
        self.player = Player(x=SCREEN_WIDTH/2,y=SCREEN_HEIGHT/2,radius=25,color=(255,0,0), speed=5)
        if gen_obstacles:
            self.obstacles = [Obstacle(SCREEN_WIDTH, SCREEN_HEIGHT, size=obs_size) for x in range(NUM_OBSTACLES)]
            # ensure player isn't colliding with obstacles
            center = np.array((self.player.x, self.player.y))
            for i, obstacle in enumerate(self.obstacles):
                inside = obstacle.inside_polygon(self.player.x, self.player.y) or obstacle.collision(center, self.player.radius)
                while inside:
                    self.obstacles[i] = Obstacle(SCREEN_WIDTH, SCREEN_HEIGHT,size=obs_size)
                    print(self.obstacles[i].size)
                    inside = self.obstacles[i].inside_polygon(self.player.x, self.player.y) or self.obstacles[i].collision(center, self.player.radius)[0]
                    print(inside)

        self.entities = [self.player]
        
        # for i in range(30):
        #     self.generate_AI()
    
    def generate_AI(self):
        edge = random.randint(0,3)
        xy = get_ai_spawn_location(edge, self.obstacles)
        self.entities.append(RandomAI(
                 x=xy[0]
                ,y=xy[1]
                ,radius=random.randrange(MIN_RADIUS,MAX_RADIUS)
                ,color=(0,200,20)
                ,speed=random.randrange(2,5)
        ))

        edge = random.randint(0,3)
        xy = get_ai_spawn_location(edge, self.obstacles)
        self.entities.append(SimpleAI(
                 x=xy[0]
                ,y=xy[1]
                ,radius=random.randrange(MIN_RADIUS,MAX_RADIUS)
                ,color=(0,50,200)
                ,speed=random.randrange(2,5)
                ))

        edge = random.randint(0,3)
        xy = get_ai_spawn_location(edge, self.obstacles)
        self.entities.append(RRTAI(
                x=xy[0]
               ,y=xy[1]
               ,radius=random.randrange(MIN_RADIUS,MAX_RADIUS)
               ,color=(200,200,20)
               ,speed=random.randrange(5,7)
               ,maxwidth=SCREEN_WIDTH
               ,maxheight=SCREEN_HEIGHT
        ))

    def __str__(self):
        return ''
    
    def update(self, controller):
        if controller.quit:
            pygame.quit()
            sys.exit()
        if self.lost and controller.space:
            self.lost = False
            self.__init__(gen_obstacles=False)
        if self.lost and controller.tab:
            self.lost = False
            self.__init__(gen_obstacles=True)

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
                break


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
        self.lose_text2 = self.lose_font.render("Press SPACE to try again with the same map", True, self.font_color)
        self.lose_text2rect = self.lose_text2.get_rect(center = (SCREEN_WIDTH/2, (SCREEN_HEIGHT/2)))
        self.lose_text3 = self.lose_font.render("Press TAB to try again with a new map", True, self.font_color)
        self.lose_text3rect = self.lose_text3.get_rect(center = (SCREEN_WIDTH/2, (SCREEN_HEIGHT/2)+65))

    def display(self, model):
        self.screen.fill(self.background_color)
        for obstacle in model.obstacles:
            obstacle.display(self.screen)
        for entity in model.entities:
            entity.display(self.screen)
        if not model.lost:
            self.elapsed_time = model.passed_time
        else:
            self.screen.blit(self.lose_text1, self.lose_text1rect)
            self.screen.blit(self.lose_text2, self.lose_text2rect)
            self.screen.blit(self.lose_text3, self.lose_text3rect)
        
#        if model.debug:
#            model.roadmap.display(self.screen)
            
        timer = self.font.render("Time(s): {0:.1f}".format(self.elapsed_time), True, self.font_color)
        ai_spawned = self.font.render("AI Spawned: " + str(len(model.entities)-1), True, self.font_color)
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
    K_TAB,
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
    tab = False
    
    def update(self):
        self.player_down = False
        self.player_up = False
        self.player_left = False
        self.player_right = False        
        self.space = False
        self.tab = False
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
        if keys[K_TAB]:
            self.tab = True
       
                
if __name__ == '__main__':
    import main