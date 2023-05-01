from CircleEntity import CircleEntity
from SimpleAI import SimpleAI
from Obstacle import check_collision
import heapq
import pygame
import numpy as np
import random
import math
from pprint import pprint
import copy

def normalized(a, axis=-1, order=2):
    l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
    l2[l2==0] = 1
    return (a / np.expand_dims(l2, axis))[0]

def gen_random_move(R, cx, cy):
        r = R*math.sqrt(random.random())
        theta = random.random() * 2 * math.pi
        x = cx + r*math.cos(theta)
        y = cy + r*math.sin(theta)
        return np.array((x, y))



# Define a function to compute the Euclidean distance between two points
def distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def get_neighbors(node, tree):
    return [child for child, parent in tree.items() if parent == node]

# Define the A* algorithm to find the optimal path from the start to the goal
def astar(start, goal, tree):
    frontier = [(distance(start, goal), start)]
    came_from = {start: None}
    cost_so_far = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        if np.array_equal(current, goal):
            path = []
            while current is not None:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        children = tree.get(current, [])

        for child in children:
            new_cost = cost_so_far[current] + distance(current, child)  # assuming all edges have unit cost
            if child not in cost_so_far or new_cost < cost_so_far[child]:
                cost_so_far[child] = new_cost
                priority = new_cost + distance(child, goal)
                heapq.heappush(frontier, (priority, child))
                came_from[child] = current

    return []  # no path found

from queue import PriorityQueue
       
class RRTAI(CircleEntity):
    def __init__(self, x, y, radius, color,speed, maxwidth, maxheight, v_x=0, v_y=0):
        super().__init__(x, y, radius, color, speed, v_x, v_y)
        self.iter = 0
        self.x_max = maxwidth
        self.y_max = maxheight
        self.x_min = 0
        self.y_min = 0
        self.maxdistance = 200
        self.tree_speed = speed*14
        self.tree = {(x,y):[]}
        self.path = None
        self.nearest_node = None # the node in the tree closest to the player
        self.reached_node = False
        self.maxiter = 100
        self.dir = (0,0)
        self.reached_goal = False
        self.path = [(x,y)]

    # returns direction to next node
    def get_direction(self):
        if self.path == [] or self.path == None:
            return np.array((0,0))
        #compute direction from current position to next point on the node
        dir = np.array((self.path[0][0] - self.x, self.path[0][1]-self.y))
        return dir
    
    def add_to_tree(self, n1, n2):
        n1_list = self.tree.get(tuple(n1), [])
        if n1_list is not None and tuple(n2) not in n1_list:
            n1_list.append(tuple(n2))
            self.tree[tuple(n1)] = n1_list
        n2_list = self.tree.get(tuple(n2), [])
        if n2_list is not None and tuple(n2) not in n2_list:
            n2_list.append(tuple(n1))
            self.tree[tuple(n2)] = n2_list

    def update(self, obstacles, player):
        goal = np.array((player.x, player.y))
        # check closest node to player
        min_dist = float('inf')
        #pprint(self.tree)
        for node in self.tree:
            dist = np.linalg.norm(np.array(node) - goal)
            if dist < min_dist:
                min_dist = dist
                self.nearest_node = node

        if (self.reached_goal):
            # make 1 new node
            self.reached_node = False
            self.reached_goal = False
            rand = np.array([np.random.uniform(self.x_min, self.x_max), np.random.uniform(self.y_min, self.y_max)])
        
            nearest_node = None
            min_dist = float('inf')
            for node in self.tree:
                dist = np.linalg.norm(np.array(node) - rand)
                #print('node', node, dist)
                if dist < min_dist:
                    min_dist = dist
                    nearest_node = node

            new_node = np.array(nearest_node) + self.tree_speed * (rand - np.array(nearest_node)) / min_dist
            if tuple(new_node) not in self.tree and not any([new_node[0] > self.x_max, new_node[0] < self.x_min, new_node[1] > self.y_max, new_node[1] < self.y_min]):
                collision = check_collision(new_node, self.radius*2, obstacles)
                if not collision:
                    self.add_to_tree(new_node, nearest_node)
                    if np.linalg.norm(new_node - goal) <= self.tree_speed:
                        self.add_to_tree(new_node, goal)
            #with the new node, create a new path from curr position to the nearest node to player
            self.path = astar((self.x,self.y), self.nearest_node, self.tree)
            if self.path == []:
                self.reached_goal = True
            self.dir = self.get_direction()
        else:
            #check if you're at your current target goal node
            if (self.reached_node):
                self.reached_node=False
                #if you are, advance along the path by 1
                self.path.pop(0)
                if len(self.path) == 0:
                    self.reached_goal = True
            
            #if you're not at the goal keep moving in the direction towards the goal
            self.dir = self.get_direction()
            if self.dir is None:
                return 0
            elif (np.linalg.norm(self.dir)) < self.speed:
                #print('dir', dir)
                self.v_x = self.dir[0]
                self.v_y = self.dir[1]
                self.reached_node = True
            else:
                norm_dir = normalized(self.dir)
                speed_dir = norm_dir * self.speed
                self.v_x = speed_dir[0]
                self.v_y = speed_dir[1]
        
        super().update(obstacles)

        temp_x = player.x - self.x
        temp_y = player.y - self.y
        dist = math.sqrt(temp_x**2 + temp_y**2)
        if dist < self.radius:
            return 1
        return 0
        
                
    def display(self, screen):
        for node, children in self.tree.items():
           pygame.draw.circle(screen, (128,128,128), node, self.radius/3)
           for child in children:
               pygame.draw.line(screen, (128,128,128), node, child)
        pygame.draw.circle(screen, (0,255,50), self.nearest_node, self.radius/3)
        
        super().display(screen)



if __name__ =='__main__':
    import main

