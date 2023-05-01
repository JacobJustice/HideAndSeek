from CircleEntity import CircleEntity
from SimpleAI import SimpleAI
import heapq
import pygame
import numpy as np
import random
import math
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

# Define the A* algorithm to find the optimal path from the start to the goal
def astar(nearest, start, goal, tree):
    #insert start and goal into the tree
    tree[tuple(goal)] = nearest
    # Initialize the open and closed sets
    open_set = [(0, start)]
    closed_set = set()

    # Initialize the g score and f score for each node
    g_score = {start: 0}
    f_score = {start: distance(start, goal)}

    while len(open_set) > 0:
        # Get the node with the lowest f score from the open set
        current = heapq.heappop(open_set)[1]

        # Check if the current node is the goal
        if np.array_equal(current, goal):
            # Reconstruct the optimal path from the start to the goal
            path = [current]
            while current in tree:
                print('current',current)
                current = tree[current]
                path.append(current)
            return path[-1]

        # Add the current node to the closed set
        closed_set.add(current)

        # Check the neighbors of the current node
        for neighbor in tree:
            if neighbor in closed_set:
                continue

            # Compute the tentative g score for the neighbor
            tentative_g_score = g_score[current] + distance(current, neighbor)

            # If the neighbor is not in the open set, add it
            if neighbor not in [x[1] for x in open_set]:
                heapq.heappush(open_set, (f_score.get(neighbor, float('inf')), neighbor))

            # If the tentative g score is greater than the current g score for the neighbor, skip it
            elif tentative_g_score >= g_score.get(neighbor, float('inf')):
                continue

            # Otherwise, update the g score and f score for the neighbor
            tree[neighbor] = current
            g_score[neighbor] = tentative_g_score
            f_score[neighbor] = tentative_g_score + distance(neighbor, goal)

    # If the goal is not reachable, return an empty path
    return []

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
    def get_direction(self, nearest_node, goal, obstacles):
        print('get dir')
        # if that node is the same node as previous, continue along path
        # if that node is different, recompute path
        if nearest_node is not self.nearest_node:
            self.nearest_node = nearest_node
            copytree = copy.deepcopy(self.tree)
            self.path = astar(nearest_node, (self.x,self.y), goal, copytree)

        if self.path == [] or self.path == None:
            return np.array((0,0))
        #compute direction from current position to next point on the node
        print('path', self.path)
        dir = np.array((self.path[0][0] - self.x, self.path[0][1]-self.y))
        print(self.nearest_node, self.x,self.y, self.reached_node)
        if self.reached_node and len(self.path) > 1:
            print("reached")
            self.path.pop(0)
            dir = np.array((self.path[0][0] - self.x, self.path[0][1]-self.y))
        return normalized(dir)

    def update(self, obstacles, player):
        goal = np.array((player.x, player.y))
        # check closest node to player
        goal_nearest_node = None
        min_dist = float('inf')
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
                    self.tree[tuple(new_node)] = tuple(nearest_node)

                    if np.linalg.norm(new_node - goal) <= self.tree_speed:
                        self.tree[tuple(goal)] = tuple(new_node)
            self.iter += 1
        
        #get direction
        print(self.path)
        dir = self.get_direction(goal_nearest_node, goal, obstacles)
        if dir is None:
            return 0
        #scale direction by speed, or by remaining distance to next node
        if (np.linalg.norm(dir)) < self.speed:
            print('dir', dir)
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
        
        return 0
        
                
    def display(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        for node in self.tree:
            pygame.draw.circle(screen, (128,128,128), node, self.radius/3)
        pygame.draw.circle(screen, (0,255,50), self.nearest_node, self.radius/3)


if __name__ =='__main__':
    import main

