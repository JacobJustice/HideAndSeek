from CircleEntity import CircleEntity
import random
import math

def normalize(x, y, speed=1):
    t = (x, y)
    norm_squared = sum([x**2 for x in t])
    norm = math.sqrt(norm_squared)
    normalized_t = tuple([(x/norm)*speed for x in t])
    return normalized_t

class SimpleAI(CircleEntity):
    complex = False
    def __init__(self, x, y, radius, color,speed, v_x=0, v_y=0):
        super().__init__(x, y, radius, color, speed, v_x, v_y)

    def update(self, obstacles, player):
        super().update(obstacles)
        temp_x = player.x - self.x
        temp_y = player.y - self.y

        dist = math.sqrt(temp_x**2 + temp_y**2)
        if dist < self.radius:
            return 1

        self.v_x, self.v_y = normalize(temp_x, temp_y,self.speed)
        return 0

