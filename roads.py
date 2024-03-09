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

print("helooooooooo", heightmap[86 - areaLow[0]][13 - areaLow[2]])

def buildRoads(buildings):
    obstacles = []
    doors = []
    goals = []
    for b in buildings:
        doors.append(b.door)

    print(len(buildings))
    for building in buildings:
        print(building.corner.x - 1, building.corner.x + building.length)
        print(building.corner.z - 1, building.corner.z + building.width)
        for x in range(building.corner.x - 1, building.corner.x + building.length + 1):
            for z in range(building.corner.z - 1, building.corner.z + building.width + 1):
                obstacles.append(Point(x, building.corner.y, z))
                print(x, building.corner.y, z)
        print(building.door.x, building.door.y, building.door.z - 1)
        obstacles.remove(Point(building.door.x, building.door.y, building.door.z - 1))
        obstacles.remove(Point(building.door.x, building.door.y, building.door.z))
    print(obstacles)

    pts = lsrl(doors)
    #editor.placeBlock((pts[0].x, pts[0].y, pts[0].z), Block("red_concrete"))
    #editor.placeBlock((pts[1].x, pts[1].y, pts[1].z), Block("red_concrete"))
    highway = astar(pts[0], pts[1], obstacles)
    for block in highway:
        print("placing block at:", block.pos.x, block.pos.y, block.pos.z)
        goals.append(block.pos)
        editor.placeBlock((block.pos.x, block.pos.y, block.pos.z), Block("red_concrete"))
        #editor.placeBlock((block.pos.x, block.pos.y, block.pos.z), Block("grass_block"))

    for building in buildings:
        path = astar(building.door, findNearest(building.door, goals), obstacles)
        print("path built")
        for block in path:
            print("placing block at:", block.pos.x, block.pos.y, block.pos.z)
            editor.placeBlock((block.pos.x, block.pos.y, block.pos.z), Block("red_concrete"))
            #editor.placeBlock((block.pos.x, block.pos.y, block.pos.z), Block("grass_block"))
    """
    print("building roads")
    for building in buildings:
        path = astar(building.door, findNearest(building.door, goals), obstacles)
        print("path built")
        for block in path:
            print("placing block at:", block.pos.x, block.pos.y, block.pos.z)
            goals.append(block.pos)
            editor.placeBlock((block.pos.x, block.pos.y, block.pos.z), Block("red_concrete"))
            #editor.placeBlock((block.pos.x, block.pos.y, block.pos.z), Block("grass_block"))"""

def findNearest(pos, goals):
    print(pos.x, pos.y, pos.z)
    print(goals[0].x, goals[0].y, goals[0].z, "and", goals[1].x, goals[1].y, goals[1].z)
    best = None
    bestDistance = float('inf')
    for goal in goals:
        dist = abs(pos.x - goal.x) + abs(pos.y - goal.y) + abs(pos.z - goal.z)
        if dist < bestDistance and pos != goal:
            best = goal
            bestDistance = dist
    print("best", best.x, best.y, best.z)
    return best

def lsrl(points):
    xValues = np.array([i.x for i in points])
    zValues = np.array([i.z for i in points])
    r = np.corrcoef(xValues, zValues)[0, 1]
    slope = r * (np.std(zValues)/np.std(xValues))

    xlow = np.min(xValues) + 5
    zlow = int(np.mean(zValues) - slope * np.mean(xValues) + slope * xlow)
    ylow = heightmap[xlow - areaLow[0]][zlow - areaLow[2]] - 1
    xhigh = np.max(xValues) - 5
    zhigh = int(np.mean(zValues) - slope * np.mean(xValues) + slope * xhigh)
    yhigh = heightmap[xhigh - areaLow[0]][zhigh - areaLow[2]] - 1
    return [Point(xlow, ylow, zlow), Point(xhigh, yhigh, zhigh)]

def astar(first, goal, obstacles):
    print("pathing from", first.x, first.y, first.x, "to", goal.x, goal.y, goal.z)
    queue = PriorityQueue()
    start = Node(first, None, goal)
    closed = []
    open = [start.pos]
    queue.put(start)

    while not queue.empty():
        current = queue.get()
        open.remove(current.pos)
        #editor.placeBlock((current.pos.x, current.pos.y, current.pos.z), Block("grass_block"))
        print("heuristic:", current.h, "f:", current.f, "point:", current.pos.x, current.pos.y, current.pos.z)
        if current.h == 0:
            path = []
            current = current.parent
            while current.parent is not None:
                path.append(current)
                current = current.parent
            path.reverse()

            return path

        closed.append(current.pos)
        for neighbor in current.possibleBlocks():
            print("in obstables:", neighbor in obstacles)
            if neighbor not in obstacles and neighbor not in closed:
                """new = Node(neighbor, current, goal)
                if new in queue: 
                    #if (new.g + new.e) < ()
                    pass"""
                if neighbor in open: # implement this later for better functionality
                    pass
                else:
                    print("##### new node", neighbor.x, neighbor.y, neighbor.z)
                    print("open", len(open), "queue", queue.qsize())
                    queue.put(Node(neighbor, current, goal))
                    open.append(neighbor)
                    #time.sleep(0.5)

    return None

class Node:
    def __init__(self, pos, parent, goal):
        self.pos = pos
        self.goal = goal
        self.h = abs(self.goal.x - pos.x) + abs(self.goal.z - pos.z)
        self.g = 0
        self.e = 0
        self.parent = parent

        if parent is not None:
            self.g = parent.g + 1
            self.e = parent.e + 2 * abs(parent.pos.y - self.pos.y)

        self.f = self.g + self.h + self.e

    def __lt__(self, other):
        return self.f < other.f

    def __eq__(self, other):
        return self.pos == other.pos

    def possibleBlocks(self):
        blocks = []
        """blocks.append(Point(self.pos.x + 1, self.pos.y, self.pos.z))
        blocks.append(Point(self.pos.x, self.pos.y, self.pos.z + 1))
        blocks.append(Point(self.pos.x - 1, self.pos.y, self.pos.z))
        blocks.append(Point(self.pos.x, self.pos.y, self.pos.z - 1))"""
        print("hi")

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