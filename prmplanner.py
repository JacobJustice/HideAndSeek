# prmplanner.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to Clemson University and the authors.
# 
# Author: Ioannis Karamouzas (ioannis@g.clemson.edu)

# Modified for use in my final project

from graph import RoadmapVertex, RoadmapEdge, Roadmap
from utils import *
import math
import random

def generate_configurations(N,maxX=1, maxY=1):
    coords = []
    for i in range(N):
        x = random.uniform(0, maxX)
        y = random.uniform(0, maxY)
        coords.append((x, y))
    return coords

def connect_sample(graph, vert, neighbors, radius, obstacles):
    neighbors = k_nearest_neighbors(graph, vert, K=5)
    for neighbor, dist in neighbors:
        path = interpolate(vert.getConfiguration(), neighbor.getConfiguration(), stepsize=1)
        collide=False
        for point in path:
            if collision(point, radius, obstacles):
                collide=True
                break
        if not collide:
            graph.addEdge(vert, neighbor, dist, path=[vert.getConfiguration()
                                                    , neighbor.getConfiguration()])
    return graph

def build_roadmap(q_range, radius, obstacles):
    # the roadmap 
    graph = Roadmap()

    configs = generate_configurations(100, q_range[0], q_range[1])

    # test configurations for collisions and keep collision free samples
    for vert in configs:
        if not collision(vert, radius, obstacles):
            graph.addVertex(vert)

    # connect each sample to its nearest neighbor and maintain only collision-free links
    vert_edges = []
    for i, vert in enumerate(graph.getVertices()):
        print(i)
        connect_sample(graph, vert, k_nearest_neighbors(graph, vert, K=5), radius, obstacles)

    return graph
  
def find_path(q_start, q_goal, graph, radius, obstacles):
    if collision(q_start, radius, obstacles) or collision(q_goal, radius, obstacles):
        return None
    # add q_start add q_goal to graph
    graph.addVertex(q_start)
    start_vert = graph.getVertices()[-1]
    connect_sample(graph, start_vert, start_neighbors:=k_nearest_neighbors(graph, start_vert, K=1), radius, obstacles)
    graph.addVertex(q_goal)
    goal_vert = graph.getVertices()[-1]
    connect_sample(graph, goal_vert, goal_neighbors:=k_nearest_neighbors(graph, goal_vert, K=1), radius, obstacles)
    #print(start_vert.getEdges())

    path  = [start_vert.getConfiguration()] 
    
     # Use the OrderedSet for your closed list
    closed_set = OrderedSet()
    
    # Use the PriorityQueue for the open list
    open_set = PriorityQueue(order=min, f=lambda v: v.f)      

    g = 0
    h = distance(q_start, q_goal)
    f = g+h

    open_set.put(start_vert, Value(f=f, g=g))
    parent = {}

    while len(open_set) > 0:
        vert, value = open_set.pop()
        config = vert.getConfiguration()
        if config == q_goal:
            break
        closed_set.add(vert.id)

        #for all possible actions
        for edge in vert.getEdges():
            dest_vert = graph.getVertices()[edge.dest_id]
            dest_config = dest_vert.getConfiguration()
            if edge.dest_id in closed_set:
                continue
            tentative_gscore = value.g + edge.getDist()
            h = abs(dest_config[0] - q_goal[0]) + abs(dest_config[1] - q_goal[1])
            f = tentative_gscore+h

            if dest_vert not in open_set or (dest_vert in open_set and open_set.get(dest_vert).f > f):
                open_set.put(dest_vert, Value(f=f, g=tentative_gscore))
                parent.update({dest_vert:vert})
    
    path = []
    cur_node = vert
    while cur_node.getConfiguration() != q_start:
        path.insert(0, np.array(cur_node.getConfiguration()))
        cur_node = parent[cur_node]

    return path


# ----------------------------------------
# below are some functions that you may want to populate/modify and use above 
# ----------------------------------------

def nearest_neighbors(graph, q, max_dist=10.0, q_is_tuple=False):
    """
        Returns all the nearest roadmap vertices for a given configuration q that lie within max_dist units
        You may also want to return the corresponding distances 
    """
    neighbors = []
    dists = []
    for vertex in graph.getVertices():
        if q_is_tuple:
            dist = distance(q, vertex.getConfiguration())
        else:
            dist = distance(q.getConfiguration(), vertex.getConfiguration())
        if dist > 0.0001 and dist < max_dist:
            neighbors.append(vertex)
            dists.append(dist)
    return neighbors, dists

def k_nearest_neighbors(graph, q, K=10, q_is_tuple=False):
    """
        Returns the K-nearest roadmap vertices for a given configuration q. 
        You may also want to return th corresponding distances 
    """
    neighbors, dists = nearest_neighbors(graph, q, max_dist=9999.0, q_is_tuple=q_is_tuple)
    lowest_dists = [(None, float('inf')) for k in range(K)]
    for neighbor, dist in zip(neighbors, dists):
        if dist < lowest_dists[-1][1]:
            lowest_dists.pop()
            lowest_dists.append((neighbor, dist))
            lowest_dists.sort(key=lambda x: x[1])
    return [x for x in lowest_dists if x[0] is not None]

def distance (q1, q2): 
    """
        Returns the distance between two configurations. 
        You may want to look at the getRobotPlacement function in utils.py that returns the OBB for a given configuration  
    """
    return math.sqrt((q2[0]-q1[0])**2 + (q2[1]-q1[1])**2)

def closest_point(q, aabb_min, aabb_max):
    """
    returns the closest point in the AABB to q
    min is the x_min and y_min as a tuple (x_min, x_max)
    max is the same for the maxes
    """
    x_clamp = max(aabb_min[0], min(q[0], aabb_max[0]))
    y_clamp = max(aabb_min[1], min(q[1], aabb_max[1]))
    return (x_clamp, y_clamp)

def collision(q, circle, obstacles):
    """
        Determines whether the robot placed at configuration q will collide with the list of AABB obstacles.  
    """
    for obstacle in obstacles:
        if obstacle.collision(q, circle)[0] or obstacle.inside_polygon(q[0], q[1]):
            return True
    return False 


def interpolate (q1, q2, stepsize):
    """
        Returns an interpolated local path between two given configurations. 
        It can be used to determine whether an edge between vertices is collision-free. 
    """
    dist = distance(q1, q2)
    num_steps = int(dist/stepsize)+1
    path = []

    for i in range(num_steps):
        step = i/num_steps
        step_1 = 1-step
        p1 = (step_1*q1[0], step_1*q1[1])
        p2 = (step*q2[0], step*q2[1])
        path.append((p1[0]+p2[0], p1[1]+p2[1]))

    return path
