# Import the pygame module
import pygame
from MVC import Model, View, Controller, SCREEN_HEIGHT, SCREEN_WIDTH

# Initialize pygame
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

running = True
model = Model()
print(model)
view = View(screen)
controller = Controller()

# Main loop
while model.running:
    controller.update()
    model.update(controller)
    view.display(model)
