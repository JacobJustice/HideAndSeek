import math
import random
import numpy as np

# randomly generates nicely shaped polygons
# such that all vertices are the result of randomly angled steps around a circle
# has irregularity and spikiness parameters that affect the shape of the polygon

def random_angle_steps(steps: int, irregularity: float):
    angles = []
    lower = (2 * math.pi / steps) - irregularity
    upper = (2 * math.pi / steps) + irregularity
    cumsum = 0
    for i in range(steps):
        angle = random.uniform(lower, upper)
        angles.append(angle)
        cumsum += angle

    cumsum /= (2 * math.pi)
    for i in range(steps):
        angles[i] /= cumsum
    return angles

def clip(value, lower, upper):
    return min(upper, max(value, lower))
    
def generate_polygon(center, avg_radius: float,
                     irregularity: float, spikiness: float,
                     num_vertices: int):
    # Parameter check
    if irregularity < 0 or irregularity > 1:
        raise ValueError("Irregularity must be between 0 and 1.")
    if spikiness < 0 or spikiness > 1:
        raise ValueError("Spikiness must be between 0 and 1.")

    irregularity *= 2 * math.pi / num_vertices
    spikiness *= avg_radius
    angle_steps = random_angle_steps(num_vertices, irregularity)

    # now generate the points
    points = []
    angle = random.uniform(0, 2 * math.pi)
    for i in range(num_vertices):
        radius = clip(random.gauss(avg_radius, spikiness), 0, 2 * avg_radius)
        point = (center[0] + radius * math.cos(angle),
                        center[1] + radius * math.sin(angle))
        points.append(point)
        angle += angle_steps[i]

    return np.array(points)
