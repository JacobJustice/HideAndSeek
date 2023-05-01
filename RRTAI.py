from CircleEntity import CircleEntity
from SimpleAI import SimpleAI
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

def check_collision(pos, radius, obstacles):
    for obstacle in obstacles:
         if obstacle.collision(pos, radius)[0] or obstacle.inside_polygon(pos[0],pos[1]):
            return True
    return False


# Define a function to compute the Euclidean distance between two points
def distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def get_neighbors(node, tree):
    return [child for child, parent in tree.items() if parent == node]

# Define the A* algorithm to find the optimal path from the start to the goal
def astar(nearest, start, goal, tree):
    #insert goal into the tree
    tree[tuple(goal)] = nearest

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
            print("path", path)
            return path[::-1]

        children = get_neighbors(current, tree)
        print(children)

        for child in children:
            new_cost = cost_so_far[current] + distance(current, child)  # assuming all edges have unit cost
            if child not in cost_so_far or new_cost < cost_so_far[child]:
                cost_so_far[child] = new_cost
                priority = new_cost + distance(child, goal)
                heapq.heappush(frontier, (priority, child))
                came_from[child] = current

    return None  # no path found

class RRTAI(SimpleAI):
    def __init__(self, x, y, radius, color,speed, maxwidth, maxheight, v_x=0, v_y=0):
        super().__init__(x, y, radius, color, speed, v_x, v_y)
        self.iter = 0
        self.x_max = maxwidth
        self.y_max = maxheight
        self.x_min = 0
        self.y_min = 0
        self.tree_speed = speed*14
        self.tree = {(x,y):None}
        self.path = None
        self.nearest_node = None
        self.reached_node = False
        self.maxiter = 100

    # returns direction to next node
    def get_direction(self, goal_nearest, goal, obstacles):
        #print('get dir')
        # if that node is the same node as previous, continue along path
        # if that node is different, recompute path
        if goal_nearest is not self.nearest_node:
            self.nearest_node = goal_nearest
            start_nearest = None
            min_dist = float('inf')
            #pprint(self.tree)
            start = np.array((self.x, self.y))
            for node in self.tree:
                dist = np.linalg.norm(np.array(node) - start)
                if dist < min_dist:
                    min_dist = dist
                    start_nearest = node
            copytree = copy.deepcopy(self.tree)
            copytree[(self.x, self.y)] = start_nearest
            self.path = astar(goal_nearest, (self.x,self.y), goal, copytree)

        #print('path', self.path)
        if self.path == [] or self.path == None:
            return np.array((0,0))
        #compute direction from current position to next point on the node
        dir = np.array((self.path[0][0] - self.x, self.path[0][1]-self.y))
        #print(self.nearest_node, self.x,self.y, self.reached_node)
        if self.reached_node and len(self.path) > 1:
            print("reached")
            self.path.pop(0)
            print(self.path)
            dir = np.array((self.path[0][0] - self.x, self.path[0][1]-self.y))
        return dir

    def update(self, obstacles, player):
        goal = np.array((player.x, player.y))
        # check closest node to player
        goal_nearest_node = None
        min_dist = float('inf')
        #pprint(self.tree)
        for node in self.tree:
            dist = np.linalg.norm(np.array(node) - goal)
            if dist < min_dist:
                min_dist = dist
                goal_nearest_node = node

        if self.iter < self.maxiter:
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
                collision = False
                for obs in obstacles:
                    if check_collision(new_node, self.radius, obstacles):
                        collision = True
                        break
                if not collision:
                    #print("NEAREST", nearest_node)
                    self.tree[tuple(new_node)] = tuple(nearest_node)
                    #print(self.tree[tuple(new_node)])

                    if np.linalg.norm(new_node - goal) <= self.tree_speed:
                        self.tree[tuple(goal)] = tuple(new_node)
            self.iter += 1
        
        #get direction
        #print(self.path)
        dir = self.get_direction(goal_nearest_node, goal, obstacles)
        if dir is None:
            return 0
        #scale direction by speed, or by remaining distance to next node
        if (np.linalg.norm(dir)) < self.speed:
            #print('dir', dir)
            self.v_x = dir[0]
            self.v_y = dir[1]
            self.reached_node = True
        else:
            norm_dir = normalized(dir)
            speed_dir = norm_dir * self.speed
            self.v_x = speed_dir[0]
            self.v_y = speed_dir[1]
        
        collide = super().update(obstacles, player)
        
        return collide
        
                
    def display(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        for node in self.tree:
            pygame.draw.circle(screen, (128,128,128), node, self.radius/3)
        pygame.draw.circle(screen, (0,255,50), self.nearest_node, self.radius/3)


if __name__ =='__main__':
    import main

