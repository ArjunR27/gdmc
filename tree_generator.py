#!/usr/bin/env python3

"""
Load and use a world slice.
"""

import sys

import numpy as np

from gdpc import __url__, Editor, Block
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import addY
from tqdm import tqdm
import random


def draw_line(matrix, start, end):
    x1, y1 = start
    x2, y2 = end
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while x1 != x2 or y1 != y2:
        matrix[y1][x1] = 1
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    matrix[y1][x1] = 1


def rand_coord(length):
    return int(random.uniform(1, length)), int(random.uniform(1, length))


def generate_branches(length=5):
    matrices = []
    for i in range(4):
        matrices.append([[0] * length for _ in range(length)])

    draw_line(matrices[0], (0, 0), rand_coord(length))
    draw_line(matrices[1], (0, 0), rand_coord(length))
    draw_line(matrices[2], (0, 0), rand_coord(length))
    draw_line(matrices[3], (0, 0), rand_coord(length))
    return matrices


class Tree:
    def __init__(self, x, y_bot, y_top, z):
        self.x = x
        self.y_bot = y_bot
        self.y_top = y_top
        self.z = z
        self.branch_length = 5
        self.branches = generate_branches(self.branch_length)
        self.branch_count = len(self.branches)

    def place_branch(self, branch_num):

        if branch_num == 0:
            x_dir, z_dir = 1, 1
        elif branch_num == 1:
            x_dir, z_dir = 1, -1
        elif branch_num == 2:
            x_dir, z_dir = -1, -1
        else:
            x_dir, z_dir = -1, 1

        y_offset = 0
        coord = None
        for x in range(self.branch_length):
            for z in range(self.branch_length):
                if self.branches[branch_num][x][z] == 1:
                    y_offset += 1 if random.random() < 0.5 else 0
                    coord = (self.x + x_dir * x, self.y_top + y_offset, self.z + z_dir * z)
                    editor.placeBlock(coord, Block(log))

                    # Add leaves around the block
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            if i == 0 and j == 0:
                                continue
                            editor.placeBlock((coord[0] + i, coord[1], coord[2] + j), Block('oak_leaves'))

        coord = (coord[0], coord[1] + 1, coord[2])
        for i in range(-1, 2):
            for j in range(-1, 2):
                editor.placeBlock((coord[0] + i, coord[1], coord[2] + j), Block('oak_leaves'))




            # Create an editor object.
# The Editor class provides a high-level interface to interact with the Minecraft world.
editor = Editor()
# editor.buffering = True
editor.caching = True

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

# Get the build area.
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

vec = addY(buildRect.center, 30)

heightmap = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

print(f"Heightmap shape: {heightmap.shape}")

begin = buildArea.begin
end = buildArea.end

trees = []
log = 'oak_log'

for i in range(1):
    # Generate random x and z values between begin and end
    random_x = int(random.uniform(begin[0], end[0]))
    random_z = int(random.uniform(begin[2], end[2]))
    y = heightmap[random_x - begin.x - 1, random_z - begin.z - 1]

    tree = Tree(random_x, y, y + 6, random_z)
    trees.append(tree)

for tree in trees:

    for i in range(tree.branch_count):
        tree.place_branch(i)

    for y in range(tree.y_bot, tree.y_top):
        coord = (tree.x, y, tree.z)
        editor.placeBlock(coord, Block(log))
