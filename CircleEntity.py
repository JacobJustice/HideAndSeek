import pygame
import numpy as np

class CircleEntity():
    x = 0
    y = 0
    radius = 10
    color = (255,255)
    v_x = 0
    v_y = 0
    speed = 0
    
    def __init__(self, x, y, radius, color, speed,v_x=0, v_y=0):
        self.x = x 
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed
        self.v_x = v_x
        self.v_y = v_y

    def __str__(self):
        return 'x: ' + str(self.x) + ' y: ' + str(self.y) + ' radius: ' + str(self.radius) + ' color: ' + str(self.color)

    def update(self, obstacles):
        future_x = self.x+self.v_x
        future_y = self.y+self.v_y
        future_center = np.array((self.x+self.v_x, self.y+self.v_y))
        for obstacle in obstacles:
            collide, edge = obstacle.collision(future_center, self.radius)
            iters = 0
            while collide:
                normal = np.array((-edge[1], edge[0]))
                velocity = np.array((self.v_x, self.v_y))
                projection = normal * (np.dot(velocity, normal)/np.dot(normal, normal))
                new_velocity = velocity - projection
                self.v_x, self.v_y = new_velocity[0], new_velocity[1] 
                future_center = np.array((self.x+self.v_x, self.y+self.v_y))
                collide, edge = obstacle.collision(future_center, self.radius)
                iters += 1
                if iters > 5:
                    self.v_x = 0
                    self.v_y = 0
                    return

        self.x += self.v_x
        self.y += self.v_y

    def display(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        pygame.draw.line(screen, (max([self.color[0]-140,0]), max([self.color[1]-140,0]), max([self.color[2]-140, 0])), (self.x,self.y), (self.x+self.v_x*5, self.y+self.v_y*5), width=3)

