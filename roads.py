import sys
from queue import PriorityQueue
import time
from gdpc import __url__, Editor, Block
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from building import *
import numpy as np


# Create an editor object.
# The Editor class provides a high-level interface to interact with the Minecraft world.
editor = Editor()


# Check if the editor can connect to the GDMC HTTP interface.
try:
    editor.checkConnection()
except InterfaceConnectionError:
    print(
        f"Error: Could not connect to the GDMC HTTP interface at {editor.host}!\n"
        "To use GDPC, you need to use a \"backend\" that provides the GDMC HTTP interface.\n"
        "For example, by running Minecraft with the GDMC HTTP mod installed.\n"
        f"See {__url__}/README.md for more information."
    )
    sys.exit(1)

try:
    buildArea = editor.getBuildArea()
except BuildAreaNotSetError:
    print(
        "Error: failed to get the build area!\n"
        "Make sure to set the build area with the /setbuildarea command in-game.\n"
        "For example: /setbuildarea ~0 0 ~0 ~64 200 ~64"
    )
    sys.exit(1)

print("Loading world slice...")
buildRect = buildArea.toRect()
worldSlice = editor.loadWorldSlice(buildRect)
print("World slice loaded!")

heightmap = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
areaLow = buildArea.begin
areaHigh = buildArea.end

def buildRoads(buildings):
    obstacles = []
    doors = []
    goals = []

    # Adding the doors to the list
    for b in buildings:
        doors.append(b.door)

    # Adding the buildings and 1 block padding to the obstacles list
    for building in buildings:
        for x in range(building.corner.x - 1, building.corner.x + building.length + 1):
            for z in range(building.corner.z - 1, building.corner.z + building.width + 1):
                obstacles.append(Point(x, building.corner.y, z))
        obstacles.remove(Point(building.door.x, building.door.y, building.door.z - 1))
        obstacles.remove(Point(building.door.x, building.door.y, building.door.z))

    # creating the endpoints of the highway and pathing between them
    pts = lsrl(doors)
    highway = astar(pts[0], pts[1], obstacles)
    for block in highway:
        #print("placing block at:", block.pos.x, block.pos.y, block.pos.z)
        goals.append(block.pos)
        editor.placeBlock((block.pos.x, block.pos.y, block.pos.z), Block("red_concrete"))
        #editor.placeBlock((block.pos.x, block.pos.y, block.pos.z), Block("grass_block"))

    # For each building path to the nearest point on the highway to path to
    for building in buildings:
        path = astar(building.door, findNearest(building.door, goals), obstacles)
        print("path built")
        for block in path:
            print("placing block at:", block.pos.x, block.pos.y, block.pos.z)
            editor.placeBlock((block.pos.x, block.pos.y, block.pos.z), Block("red_concrete"))
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
def lsrl(points):
    # Calculating correlation coefficient and slope
    xValues = np.array([i.x for i in points])
    zValues = np.array([i.z for i in points])
    r = np.corrcoef(xValues, zValues)[0, 1]
    slope = r * (np.std(zValues)/np.std(xValues))

    # Calculating coordinates of the endpoints of the highway
    xlow = np.min(xValues) + 5
    zlow = int(np.mean(zValues) - slope * np.mean(xValues) + slope * xlow)
    ylow = heightmap[xlow - areaLow[0]][zlow - areaLow[2]] - 1
    xhigh = np.max(xValues) - 5
    zhigh = int(np.mean(zValues) - slope * np.mean(xValues) + slope * xhigh)
    yhigh = heightmap[xhigh - areaLow[0]][zhigh - areaLow[2]] - 1
    return [Point(xlow, ylow, zlow), Point(xhigh, yhigh, zhigh)]

# Astar search pathing algorithm
def astar(first, goal, obstacles):
    queue = PriorityQueue()
    start = Node(first, None, goal)
    closed = []
    open = [start.pos]
    queue.put(start)

    while not queue.empty():
        current = queue.get()
        open.remove(current.pos)

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
        for neighbor in current.possibleBlocks():
            if neighbor not in obstacles and neighbor not in closed:
                if neighbor in open: # implement this later for better functionality
                    pass
                else:
                    queue.put(Node(neighbor, current, goal))
                    open.append(neighbor)

    return None

class Node:
    def __init__(self, pos, parent, goal):
        # ALl of the parameters needed, including e which represents elevation
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
    def possibleBlocks(self):
        blocks = []
        blocks.append(Point(self.pos.x + 1, heightmap[self.pos.x + 1 - areaLow[0]][self.pos.z - areaLow[2]] - 1, self.pos.z))
        blocks.append(Point(self.pos.x, heightmap[self.pos.x - areaLow[0]][self.pos.z + 1 - areaLow[2]] - 1, self.pos.z + 1))
        blocks.append(Point(self.pos.x - 1, heightmap[self.pos.x - 1 - areaLow[0]][self.pos.z - areaLow[2]] - 1, self.pos.z))
        blocks.append(Point(self.pos.x, heightmap[self.pos.x - areaLow[0]][self.pos.z - 1 - areaLow[2]] - 1, self.pos.z - 1))
        return blocks

building1 = Building(5, 3, 6, Point(86, 63, 9))
building2 = Building(5, 4, 6, Point(76, 63, 28))
building3 = Building(5, 3, 6, Point(128, 62, 7))
building4 = Building(5, 4, 6, Point(152, 66, -12))

#buildings = [Building(7, 4, 6, Point(79, 63, 16)), Building(5, 3, 6, Point(86, 63, 9)), Building(5, 4, 6, Point(76, 63, 28))]
buildings = [building1, building2]
buildings = [building1, building3]
buildings = [building1, building4, building3, building2]
#buildings = [Building(7, 4, 6, Point(79, 63, 16)), Building(5, 3, 6, Point(86, 63, 9))]
buildRoads(buildings)