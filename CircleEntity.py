import pygame

class CircleEntity():
    x = 0
    y = 0
    radius = 10
    color = (255,255)
    v_x = 0
    v_y = 0
    
    def __init__(self, x, y, radius, color, v_x=0, v_y=0):
        self.x = x 
        self.y = y 
        self.radius = radius
        self.color = color
        self.v_x = v_x
        self.v_y = v_y

    def __str__(self):
        return 'x: ' + str(self.x) + ' y: ' + str(self.y) + ' radius: ' + str(self.radius) + ' color: ' + str(self.color)

    def update(self):
        self.x += self.v_x
        self.y += self.v_y

    def display(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

