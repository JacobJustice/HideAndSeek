from CircleEntity import CircleEntity
from SimpleAI import SimpleAI
import numpy as np
import random
import math

def normalize(x, y, speed=1):
    t = (x, y)
    norm_squared = sum([x**2 for x in t])
    norm = math.sqrt(norm_squared)
    normalized_t = tuple([(x/norm)*speed for x in t])
    return normalized_t

def gen_random_move(R, cx, cy):
        r = R*math.sqrt(random.random())
        theta = random.random() * 2 * math.pi
        x = cx + r*math.cos(theta)
        y = cy + r*math.sin(theta)
        return np.array((x, y))

def check_collision(pos, radius, obstacles):
    for obstacle in obstacles:
         if obstacle.collision(pos, radius)[0]:
            return True
    return False

class RandomAI(SimpleAI):
    def __init__(self, x, y, radius, color,speed, v_x=0, v_y=0):
        super().__init__(x, y, radius, color, speed, v_x, v_y)

    def update(self, obstacles, player):
        collision = super().update(obstacles, player)
        #generate random directions from current position, choose the one that moves you closest to the goal
        possible_moves = [gen_random_move(self.speed, self.x, self.y) for x in range(10)]
        lowest = (-1, float("inf"))
        player_center = np.array((player.x, player.y))
        center = np.array((self.x, self.y))
        for i, pos in enumerate(possible_moves):
            dist = np.linalg.norm(pos - player_center)
            check1 = dist < lowest[1]
            check2 = not check_collision(pos, self.radius, obstacles)
            if check1 and check2:
                lowest = (i, dist)
        dir = possible_moves[lowest[0]]-center
        self.v_x = dir[0]
        self.v_y = dir[1]
        
        return collision

if __name__ =='__main__':
    import main

