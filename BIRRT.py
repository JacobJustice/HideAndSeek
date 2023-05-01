import random
import math
import numpy as np

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None

class BiRRT:
    def __init__(self, start, goal, obstacle_list, max_iter=1000, step_size=0.1, goal_sample_rate=10):
        self.start = Node(start[0], start[1])
        self.goal = Node(goal[0], goal[1])
        self.obstacle_list = obstacle_list
        self.max_iter = max_iter
        self.step_size = step_size
        self.goal_sample_rate = goal_sample_rate

        self.start_tree = [self.start]
        self.goal_tree = [self.goal]

        self.path = None
        self.found_path = False

    def distance(self, n1, n2):
        return math.sqrt((n1.x - n2.x) ** 2 + (n1.y - n2.y) ** 2)

    def nearest_node(self, tree, n):
        distances = [self.distance(n, t) for t in tree]
        nearest_idx = np.argmin(distances)
        return tree[nearest_idx]

    def random_node(self):
        if random.randint(0, 100) > self.goal_sample_rate:
            x = random.uniform(0, 10)
            y = random.uniform(0, 10)
            return Node(x, y)
        else:
            return self.goal

    def is_collision_free(self, n1, n2):
        for obs in self.obstacle_list:
            if self.line_intersects_circle(n1, n2, obs[0], obs[1]):
                return False
        return True

    def line_intersects_circle(self, n1, n2, c, r):
        # Check if line segment intersects circle using vector math
        d = self.distance(n1, n2)
        v = [(n2.x - n1.x) / d, (n2.y - n1.y) / d]
        w = [(c[0] - n1.x), (c[1] - n1.y)]
        b = np.dot(w, v)
        d2 = np.dot(w, w) - b ** 2
        if d2 > r ** 2:
            return False
        elif d2 < 0:
            return True
        else:
            a = math.sqrt(r ** 2 - d2)
            t1 = b - a
            t2 = b + a
            if t1 >= 0 and t1 <= d:
                return True
            elif t2 >= 0 and t2 <= d:
                return True
            else:
                return False

    def extend(self, tree, n):
        nearest_node = self.nearest_node(tree, n)
        theta = math.atan2(n.y - nearest_node.y, n.x - nearest_node.x)
        new_x = nearest_node.x + self.step_size * math.cos(theta)
        new_y = nearest_node.y + self.step_size * math.sin(theta)
        new_node = Node(new_x, new_y)
        new_node.parent = nearest_node
        if self.is_collision_free(nearest_node, new_node):
            tree.append(new_node)
            return True
        else:
            return False

    def find_path(self):
        for i in range(self.max_iter):
            q_rand = self.random_node()

           
