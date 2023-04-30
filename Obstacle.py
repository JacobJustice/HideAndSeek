from random import randint
import random
import math
import pygame
from polygon_generator import generate_polygon
import numpy as np

def subtract_vertices(v1, v2):
    return (v1[0]-v2[0], v1[1]-v2[1])

class Obstacle:
    vertices = []
    origin = None
    always_check=False
    def __init__(self, field_width, field_height, vertices=None, origin=None, num_vertices=4, size=40) -> None:
        self.size = size + randint(0,50)
        if self.origin == None:
            self.origin = (randint(0, field_width), randint(0,field_height))
        if vertices == None:
            self.vertices = generate_polygon(self.origin, self.size, irregularity=0.1, spikiness=0.1, num_vertices=num_vertices)
        else:
            self.vertices = vertices
        
        self.color = (randint(0,255),randint(0,255),randint(0,255))


    def display(self, screen):
        pygame.draw.polygon(screen, self.color, self.vertices)
    
    def is_circle_inside_polygon(self, circle_center, radius):
        min_distance = float("inf")
        for i in range(len(self.vertices)):
            p1 = self.vertices[i]
            p2 = self.vertices[(i + 1) % len(self.vertices)]
            # Compute the distance between the center of the circle and the line containing the current side of the polygon
            distance = abs((p2[1] - p1[1]) * circle_center[0] - (p2[0] - p1[0]) * circle_center[1] + p2[0] * p1[1] - p2[1] * p1[0]) / math.sqrt((p2[1] - p1[1]) ** 2 + (p2[0] - p1[0]) ** 2)
            if distance < min_distance:
                min_distance = distance
        if min_distance < radius:
            return True
        else:
            return False
       
    def collision(self, center, circle):
        # Find the intersection points between the circle and the polygon
        intersections = []
        for i in range(len(self.vertices)):
            j = (i + 1) % len(self.vertices)
            p1 = self.vertices[i]
            p2 = self.vertices[j]
            intersection = line_circle_intersection(p1, p2, center, circle.radius)
            if intersection is not None:
                intersections.append(intersection)

        # Find the closest intersection point to the first vertex of the edge
        edge_vertex = None
        min_distance = float('inf')
        for i in range(len(self.vertices)):
            j = (i + 1) % len(self.vertices)
            for intersection in intersections:
                distance = point_line_distance(intersection, self.vertices[i], self.vertices[j])
                if distance < min_distance:
                    min_distance = distance
                    edge_vertex = self.vertices[i] - self.vertices[j]

        return True if edge_vertex is not None else False, edge_vertex

def line_circle_intersection(p1, p2, circle_center, circle_radius):
    # Find the coefficients of the quadratic equation
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    a = dx**2 + dy**2
    b = 2 * (dx * (p1[0] - circle_center[0]) + dy * (p1[1] - circle_center[1]))
    c = circle_center[0]**2 + circle_center[1]**2 + p1[0]**2 + p1[1]**2 - 2 * (circle_center[0] * p1[0] + circle_center[1] * p1[1]) - circle_radius**2

    # Find the discriminant
    discriminant = b**2 - 4 * a * c

    # If the discriminant is negative, there are no intersections
    if discriminant < 0:
        return None

    # Otherwise, find the intersection points
    t1 = (-b + math.sqrt(discriminant)) / (2 * a)
    t2 = (-b - math.sqrt(discriminant)) / (2 * a)
    intersection1 = (p1[0] + t1 * dx, p1[1] + t1 * dy)
    intersection2 = (p1[0] + t2 * dx, p1[1] + t2 * dy)

    # Return the closest intersection point to p1
    if t1 >= 0 and t1 <= 1:
        return intersection1
    elif t2 >= 0 and t2 <= 1:
        return intersection2
    else:
        return None

def point_line_distance(point, line_start, line_end):
    # Find the distance between the point and the line
    x1, y1 = line_start
    x2, y2 = line_end
    x0, y0 = point
    return abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1) / math.sqrt((y2-y1)**2 + (x2-x1)**2)

   

