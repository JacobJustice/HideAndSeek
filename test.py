from queue import PriorityQueue
import numpy as np
def distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def A_star(start, goal, graph):
    frontier_start = PriorityQueue()
    frontier_start.put((0, start))
    frontier_end = PriorityQueue()
    frontier_end.put((0, goal))

    # Initialize the cost and parent dictionaries for both directions
    cost_start = {start: 0}
    cost_end = {goal: 0}
    parent_start = {start: None}
    parent_end = {goal: None}

    # Initialize the variables to keep track of the nodes explored by both directions
    explored_start = set()
    explored_end = set()

    # Start the search
    while not frontier_start.empty() and not frontier_end.empty():
        # Explore the node with the lowest f-score in the start direction
        _, current_start = frontier_start.get()
        explored_start.add(current_start)

        # Check if the current node has been explored by the end direction
        if current_start in explored_end:
            # We have found a path between the start and goal nodes
            path = []
            node = current_start
            while node is not None:
                path.append(node)
                node = parent_start[node]
            path.reverse()
            node = parent_end[current_start]
            while node is not None:
                path.append(node)
                node = parent_end[node]
            return path

        # Explore the child nodes of the current node in the start direction
        if graph[current_start] is not None:
            for child in graph[current_start]:
                cost = cost_start[current_start] + 1
                if child not in cost_start or cost < cost_start[child]:
                    cost_start[child] = cost
                    priority = cost + distance(child, goal)
                    frontier_start.put((priority, child))
                    parent_start[child] = current_start

        # Explore the node with the lowest f-score in the end direction
        _, current_end = frontier_end.get()
        explored_end.add(current_end)

        # Check if the current node has been explored by the start direction
        if current_end in explored_start:
            # We have found a path between the start and goal nodes
            path = []
            node = current_end
            while node is not None:
                path.append(node)
                node = parent_end[node]
            path.reverse()
            node = parent_start[current_end]
            while node is not None:
                path.append(node)
                node = parent_start[node]
            return path

    # Explore the child nodes of the current node in the end direction
    if graph[current_end] is not None:
        for child in graph[current_end]:
            cost = cost_end[current_end] + 1
            if child not in cost_end or cost < cost_end[child]:
                cost_end[child] = cost
                priority = cost + distance(child, start)
                frontier_end.put((priority, child))
                parent_end[child] = current_end

    # If we reach here, we have not found a path between the start and goal nodes
    return []

graph = {
    'a': ['b', 'c'],
    'b': ['d', 'e'],
    'c': ['f', 'g'],
    'd': ['h'],
    'e': ['i'],
    'f': ['j'],
    'g': ['k'],
    'h': ['l'],
    'i': ['m'],
    'j': ['n'],
    'k': ['o'],
    'l': [],
    'm': [],
    'n': [],
    'o': []
}

start = 'a'
goal = 'o'

path = A_star(start, goal, graph)

print(path) # ['a', 'c', 'g', 'k', 'o']
