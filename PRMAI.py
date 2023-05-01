from CircleEntity import CircleEntity
import random
import math
import pygame
import copy
from prmplanner import *
from utils import *

debug = True
   
def normalized(a, axis=-1, order=2):
    l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
    l2[l2==0] = 1
    return (a / np.expand_dims(l2, axis))[0]

def same_vert(vert1, vert2):
    return vert1[0] == vert2[0] and vert1[1] == vert2[1]

class PRMAI(CircleEntity):
    on_roadmap = False
    chasing = False
    closest_vertex = None #closest vertex to the player
    complex = True
    reached_node = None
    path = []
    def __init__(self, x, y, radius, color, speed, v_x=0, v_y=0, screen=None):
        super().__init__(x, y, radius, color, speed, v_x, v_y)
    
    # returns direction to next node
    def get_direction(self, roadmap, player, obstacles):
        closest_vert = k_nearest_neighbors(roadmap, (player.x, player.y), K=1, q_is_tuple=True)[0]
        #print('closest',closest_vert, self.closest_vertex)
        #print(self.path, closest_vert)
        if (self.reached_node):
            print('reached node')
            self.path.pop(0)
        # get a path to the player using the roadmap
        if self.path is None or len(self.path) == 0 or (self.closest_vertex is not None and same_vert(self.closest_vertex, closest_vert)):
            self.closest_vertex = closest_vert
            copy_roadmap = copy.deepcopy(roadmap)
            self.path = find_path((self.x, self.y), (player.x, player.y), copy_roadmap, self.radius, obstacles)

        if self.path is None or len(self.path) == 0:
            return None
        else:
            return np.array((self.path[0][0] - self.x, self.path[0][1]-self.y))

    def update(self, roadmap, player, obstacles):
        temp_x = player.x - self.x
        temp_y = player.y - self.y

        dist = math.sqrt(temp_x**2 + temp_y**2)
        if dist < self.radius:
            return 1

        #get direction
        dir = self.get_direction(roadmap, player, obstacles)
        if dir is None:
            return 0
        #scale direction by speed, or by remaining distance to next node
        if (np.linalg.norm(dir)) < self.speed:
            self.v_x = dir[0]
            self.v_y = dir[1]
            self.reached_node = True
        else:
            norm_dir = normalized(dir)
            print('norm_dir', norm_dir)
            speed_dir = norm_dir * self.speed
            print('speed_dir', speed_dir)
            self.v_x = speed_dir[0]
            self.v_y = speed_dir[1]
        
        super().update(obstacles)
        return 0



if __name__ == '__main__':
    import main
