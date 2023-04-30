from CircleEntity import CircleEntity

class Player(CircleEntity):
    def __init__(self, x, y, radius, color, speed, v_x=0, v_y=0):
        super().__init__(x, y, radius, color, speed, v_x, v_y)

    def update(self, obstacles, controller):
        self.v_x = 0
        self.v_y = 0
        if controller.player_up:
            self.v_y -= self.speed
        if controller.player_down:
            self.v_y += self.speed
        if controller.player_left:
            self.v_x -= self.speed
        if controller.player_right:
            self.v_x += self.speed
        
        # update position and collision checking
        super().update(obstacles)

        
