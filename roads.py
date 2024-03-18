import sys
from queue import PriorityQueue
from gdpc import __url__, Editor, Block
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from glm import ivec3

from schematics import *
import numpy as np

def buildRoads(heightmap, areaLow, buildings):
    obstacles = []
    doors = []
    goals = []

    # Adding the doors to the list
    for b in buildings:
        doors.append(b.door)

    # Adding the buildings and 1 block padding to the obstacles list
    for building in buildings:
        start = ivec3(building.start.x, building.start.y - 1, building.start.z)
        for x in range(start.x - 8, start.x + 1):
            for z in range(start.z - 8, start.z + 1):
                obstacles.append(ivec3(x, start.y, z))

        # Removing the door and block in front of it from obstacles
        obstacles.remove(building.door)
        if building.direction == "north":
            obstacles.remove(ivec3(building.door.x, building.door.y, building.door.z - 1))
        elif building.direction == "south":
            obstacles.remove(ivec3(building.door.x, building.door.y, building.door.z + 1))
        elif building.direction == "west":
            obstacles.remove(ivec3(building.door.x - 1, building.door.y, building.door.z))
        else:
            obstacles.remove(ivec3(building.door.x + 1, building.door.y, building.door.z))

    # creating the endpoints of the highway and pathing between them
    pts = lsrl(heightmap, areaLow, doors, obstacles)
    highway = astar(heightmap, areaLow, pts[0], pts[1], obstacles)
    for block in highway:
        # print("placing block at:", block.pos.x, block.pos.y, block.pos.z)
        goals.append(block.pos)
        editor.placeBlock((block.pos.x, block.pos.y, block.pos.z), Block("dirt_path"))
        # editor.placeBlock((block.pos.x, block.pos.y, block.pos.z), Block("grass_block"))

    # For each building path to the nearest point on the highway to path to
    for building in buildings:
        print("DOOOOOOOOOOR:", building.door)
        path = astar(heightmap, areaLow, building.door, findNearest(building.door, goals), obstacles)
        print("path built")
        for block in path:
            # print("placing block at:", block.pos.x, block.pos.y, block.pos.z)
            editor.placeBlock((block.pos.x, block.pos.y, block.pos.z), Block("dirt_path"))
            #editor.placeBlock((block.pos.x, block.pos.y, block.pos.z), Block("grass_block"))


# Finds the nearest element of goals to pos
def findNearest(pos, goals):
    best = None
    bestDistance = float('inf')

    # Iterate through goals to find the best
    for goal in goals:
        dist = abs(pos.x - goal.x) + abs(pos.y - goal.y) + abs(pos.z - goal.z)
        if dist < bestDistance and pos != goal:
            best = goal
            bestDistance = dist
    return best


# Calculates a least squares regression line given the points and returns two endpoints of the line
def lsrl(heightmap, areaLow, points, obstacles):
    # Calculating correlation coefficient and slope
    xValues = np.array([i.x for i in points])
    zValues = np.array([i.z for i in points])
    r = np.corrcoef(xValues, zValues)[0, 1]
    slope = r * (np.std(zValues) / np.std(xValues))

    # Calculating coordinates of the endpoints of the highway
    xlow = np.min(xValues) + 5
    zlow = int(np.mean(zValues) - slope * np.mean(xValues) + slope * xlow)
    ylow = heightmap[xlow - areaLow[0]][zlow - areaLow[2]] - 1
    xhigh = np.max(xValues) - 5
    zhigh = int(np.mean(zValues) - slope * np.mean(xValues) + slope * xhigh)
    yhigh = heightmap[xhigh - areaLow[0]][zhigh - areaLow[2]] - 1

    while ivec3(xlow, ylow, zlow) in obstacles or ivec3(xhigh, yhigh, zhigh) in obstacles:
        if ivec3(xlow, ylow, zlow) in obstacles:
            xlow += 1
            zlow = int(np.mean(zValues) - slope * np.mean(xValues) + slope * xlow)
            ylow = heightmap[xlow - areaLow[0]][zlow - areaLow[2]] - 1

        if ivec3(xhigh, yhigh, zhigh) in obstacles:
            xhigh += 1
            zhigh = int(np.mean(zValues) - slope * np.mean(xValues) + slope * xhigh)
            yhigh = heightmap[xhigh - areaLow[0]][zhigh - areaLow[2]] - 1


    return [ivec3(xlow, ylow, zlow), ivec3(xhigh, yhigh, zhigh)]


# Astar search pathing algorithm
def astar(heightmap, areaLow, first, goal, obstacles):
    queue = PriorityQueue()
    start = Node(first, None, goal)
    closed = []
    open = [start.pos]
    queue.put(start)

    while not queue.empty():
        current = queue.get()
        open.remove(current.pos)
        #print("heuristic:", current.h, current.pos)

        # If the goal is reached, backtrack the path and return
        if current.h == 0:
            path = []
            current = current.parent
            while current.parent is not None:
                path.append(current)
                current = current.parent
            path.reverse()

            return path

        closed.append(current.pos)

        # Adding new nodes to the queue
        for neighbor in current.possibleBlocks(heightmap, areaLow):
            #print("neighbor")
            if neighbor not in obstacles and neighbor not in closed:
                if neighbor in open:  # implement this later for better functionality
                    pass
                else:
                    #print("adding")
                    queue.put(Node(neighbor, current, goal))
                    open.append(neighbor)
    
    return None


class Node:
    def __init__(self, pos, parent, goal):
        # ALl the parameters needed, including e which represents elevation
        self.pos = pos
        self.goal = goal
        self.h = abs(self.goal.x - pos.x) + abs(self.goal.z - pos.z)
        self.g = 0
        self.e = 0
        self.parent = parent

        # Double counting any change in elevation to incentivize the algorithm to avoid hills
        if parent is not None:
            self.g = parent.g + 1
            self.e = parent.e + 2 * abs(parent.pos.y - self.pos.y)

        self.f = self.g + self.h + self.e

    def __lt__(self, other):
        return self.f < other.f

    def __eq__(self, other):
        return self.pos == other.pos

    # Children nodes
    def possibleBlocks(self, heightmap, areaLow):
        blocks = []

        # works for square heightmaps
        length = len(heightmap)

        if not self.pos.x + 1 - areaLow[0] >= length:
            blocks.append(
                ivec3(self.pos.x + 1, heightmap[self.pos.x + 1 - areaLow[0]][self.pos.z - areaLow[2]] - 1, self.pos.z))

        if not self.pos.z + 1 - areaLow[2] >= length:
            blocks.append(
                ivec3(self.pos.x, heightmap[self.pos.x - areaLow[0]][self.pos.z + 1 - areaLow[2]] - 1, self.pos.z + 1))

        if not self.pos.x - 1 - areaLow[0] < 0:
            blocks.append(
                ivec3(self.pos.x - 1, heightmap[self.pos.x - 1 - areaLow[0]][self.pos.z - areaLow[2]] - 1, self.pos.z))

        if not self.pos.z - 1 - areaLow[2] < 0:
            blocks.append(
                ivec3(self.pos.x, heightmap[self.pos.x - areaLow[0]][self.pos.z - 1 - areaLow[2]] - 1, self.pos.z - 1))

        return blocks

