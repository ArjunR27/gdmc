import sys
from typing import Optional, Tuple

import numpy as np
from gdpc.utils import nonZeroSign
from glm import ivec2, ivec3
from gdpc import __url__, Editor, Block, geometry
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import Y, addY, dropY, line3D, circle, fittingCylinder, loop3D, Vec3iLike, Rect
import logging
from random import randint
from termcolor import colored
from gdpc import Block, Editor
from gdpc import geometry as geo
from gdpc import minecraft_tools as mt
from gdpc import editor_tools as et
import os.path
import random
from gdpc.geometry import placeBox, placeCuboid
from gdpc import __url__, Editor, Block
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import addY, dropY
from gdpc.minecraft_tools import signBlock
from gdpc.editor_tools import placeContainerBlock
from gdpc.geometry import placeBox, placeCuboid
from foundationPlacement import createFoundation

# The minimum build area size in the XZ-plane
MIN_BUILD_AREA_SIZE = ivec2(35, 35)

# Create an editor object.
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

# Check if the build area is large enough in the XZ-plane.
if any(dropY(buildArea.size) < MIN_BUILD_AREA_SIZE):
    print(
        "Error: the build area is too small for this example!\n"
        f"It should be at least {tuple(MIN_BUILD_AREA_SIZE)} blocks large in the XZ-plane."
    )
    sys.exit(1)

# Get a world slice
print("Loading world slice...")
buildRect = buildArea.toRect()
worldSlice = editor.loadWorldSlice(buildRect)
print("World slice loaded!")

editor.buffering = False  # to visualize load

# Place an outline around the build area


heightmap = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
meanHeight = np.mean(heightmap)
groundCenter = addY(buildRect.center, meanHeight)

# Build a floating 5x9 platform in the middle of the build area.

geometry.placeRectOutline(editor, buildRect, 100, Block("blue_concrete"))


def loopArea(begin: Vec3iLike, end: Optional[Vec3iLike] = None):
    """Yields all points between <begin> and <end> (end-inclusive).
    If <end> is not given, yields all points between (0,0,0) and <begin>."""
    if end is None:
        begin, end = (0, 0, 0), begin

    for x in range(begin[0], end[0] + nonZeroSign(end[0] - begin[0]), nonZeroSign(end[0] - begin[0])):
        for y in range(begin[1], end[1] + nonZeroSign(end[1] - begin[1]), nonZeroSign(end[1] - begin[1])):
            for z in range(begin[2], end[2] + nonZeroSign(end[2] - begin[2]), nonZeroSign(end[2] - begin[2])):
                yield ivec3(x, y, z)


def print_blocks_in_cube(editor, corner1, corner2):
    # Initialize the structure list
    structure = []

    # Loop through all the blocks in the cube and append to the structure list
    for vec in loopArea(corner1, corner2):
        # Calculate relative positions
        relative_position = ivec3(vec.x - corner1.x, vec.y - corner1.y, vec.z - corner1.z)
        block = str(editor.getBlock(vec))
        # Extracting the block name without the minecraft: prefix
        block_name = block.split(":")[-1]  # Assuming block format is 'minecraft:block_name'
        structure.append((relative_position.x, relative_position.y, relative_position.z, block_name))

    # Print the structure list
    print("structure = [")
    for entry in structure:
        print(f'    {entry},')
    print("]")


def build_house(editor, start_coordinate):
    structure = [
        (0, 0, 0, 'diamond_block'),
        (0, 0, -1, 'air'),
        (0, 0, -2, 'air'),
        (0, 0, -3, 'air'),
        (0, 0, -4, 'air'),
        (0, 0, -5, 'air'),
        (0, 0, -6, 'air'),
        (0, 1, 0, 'air'),
        (0, 1, -1, 'air'),
        (0, 1, -2, 'air'),
        (0, 1, -3, 'air'),
        (0, 1, -4, 'air'),
        (0, 1, -5, 'air'),
        (0, 1, -6, 'air'),
        (0, 2, 0, 'air'),
        (0, 2, -1, 'air'),
        (0, 2, -2, 'air'),
        (0, 2, -3, 'air'),
        (0, 2, -4, 'air'),
        (0, 2, -5, 'air'),
        (0, 2, -6, 'air'),
        (0, 3, 0, 'polished_andesite_stairs[facing=north,half=bottom,shape=outer_left,waterlogged=false]'),
        (0, 3, -1, 'polished_andesite_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]'),
        (0, 3, -2, 'polished_andesite_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]'),
        (0, 3, -3, 'polished_andesite_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]'),
        (0, 3, -4, 'polished_andesite_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]'),
        (0, 3, -5, 'polished_andesite_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]'),
        (0, 3, -6, 'polished_andesite_stairs[facing=west,half=bottom,shape=outer_left,waterlogged=false]'),
        (0, 4, 0, 'air'),
        (0, 4, -1, 'air'),
        (0, 4, -2, 'air'),
        (0, 4, -3, 'air'),
        (0, 4, -4, 'air'),
        (0, 4, -5, 'air'),
        (0, 4, -6, 'air'),
        (-1, 0, 0, 'air'),
        (-1, 0, -1, 'oak_log[axis=y]'),
        (-1, 0, -2, 'oak_planks'),
        (-1, 0, -3, 'oak_door[facing=west,half=lower,hinge=right,open=false,powered=false]'),
        (-1, 0, -4, 'oak_planks'),
        (-1, 0, -5, 'oak_log[axis=y]'),
        (-1, 0, -6, 'air'),
        (-1, 1, 0, 'air'),
        (-1, 1, -1, 'oak_log[axis=y]'),
        (-1, 1, -2, 'glass'),
        (-1, 1, -3, 'oak_door[facing=west,half=upper,hinge=right,open=false,powered=false]'),
        (-1, 1, -4, 'glass'),
        (-1, 1, -5, 'oak_log[axis=y]'),
        (-1, 1, -6, 'air'),
        (-1, 2, 0, 'air'),
        (-1, 2, -1, 'oak_log[axis=y]'),
        (-1, 2, -2, 'oak_planks'),
        (-1, 2, -3, 'oak_planks'),
        (-1, 2, -4, 'oak_planks'),
        (-1, 2, -5, 'oak_log[axis=y]'),
        (-1, 2, -6, 'air'),
        (-1, 3, 0, 'polished_andesite_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]'),
        (-1, 3, -1, 'oak_log[axis=y]'),
        (-1, 3, -2, 'cobblestone'),
        (-1, 3, -3, 'cobblestone'),
        (-1, 3, -4, 'cobblestone'),
        (-1, 3, -5, 'oak_log[axis=y]'),
        (-1, 3, -6, 'polished_andesite_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]'),
        (-1, 4, 0, 'air'),
        (-1, 4, -1, 'polished_andesite_stairs[facing=west,half=bottom,shape=outer_right,waterlogged=false]'),
        (-1, 4, -2, 'polished_andesite_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]'),
        (-1, 4, -3, 'polished_andesite_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]'),
        (-1, 4, -4, 'polished_andesite_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]'),
        (-1, 4, -5, 'polished_andesite_stairs[facing=west,half=bottom,shape=outer_left,waterlogged=false]'),
        (-1, 4, -6, 'air'),
        (-2, 0, 0, 'air'),
        (-2, 0, -1, 'oak_planks'),
        (-2, 0, -2, 'air'),
        (-2, 0, -3, 'air'),
        (-2, 0, -4, 'air'),
        (-2, 0, -5, 'oak_planks'),
        (-2, 0, -6, 'air'),
        (-2, 1, 0, 'air'),
        (-2, 1, -1, 'glass'),
        (-2, 1, -2, 'air'),
        (-2, 1, -3, 'air'),
        (-2, 1, -4, 'air'),
        (-2, 1, -5, 'glass'),
        (-2, 1, -6, 'air'),
        (-2, 2, 0, 'air'),
        (-2, 2, -1, 'oak_planks'),
        (-2, 2, -2, 'air'),
        (-2, 2, -3, 'air'),
        (-2, 2, -4, 'air'),
        (-2, 2, -5, 'oak_planks'),
        (-2, 2, -6, 'air'),
        (-2, 3, 0, 'polished_andesite_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]'),
        (-2, 3, -1, 'cobblestone'),
        (-2, 3, -2, 'air'),
        (-2, 3, -3, 'air'),
        (-2, 3, -4, 'air'),
        (-2, 3, -5, 'cobblestone'),
        (-2, 3, -6, 'polished_andesite_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]'),
        (-2, 4, 0, 'air'),
        (-2, 4, -1, 'polished_andesite_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]'),
        (-2, 4, -2, 'polished_andesite'),
        (-2, 4, -3, 'polished_andesite'),
        (-2, 4, -4, 'polished_andesite'),
        (-2, 4, -5, 'polished_andesite_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]'),
        (-2, 4, -6, 'air'),
        (-3, 0, 0, 'air'),
        (-3, 0, -1, 'oak_planks'),
        (-3, 0, -2, 'air'),
        (-3, 0, -3, 'air'),
        (-3, 0, -4, 'air'),
        (-3, 0, -5, 'oak_planks'),
        (-3, 0, -6, 'air'),
        (-3, 1, 0, 'air'),
        (-3, 1, -1, 'glass'),
        (-3, 1, -2, 'air'),
        (-3, 1, -3, 'air'),
        (-3, 1, -4, 'air'),
        (-3, 1, -5, 'glass'),
        (-3, 1, -6, 'air'),
        (-3, 2, 0, 'air'),
        (-3, 2, -1, 'oak_planks'),
        (-3, 2, -2, 'air'),
        (-3, 2, -3, 'air'),
        (-3, 2, -4, 'air'),
        (-3, 2, -5, 'oak_planks'),
        (-3, 2, -6, 'air'),
        (-3, 3, 0, 'polished_andesite_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]'),
        (-3, 3, -1, 'cobblestone'),
        (-3, 3, -2, 'air'),
        (-3, 3, -3, 'air'),
        (-3, 3, -4, 'air'),
        (-3, 3, -5, 'cobblestone'),
        (-3, 3, -6, 'polished_andesite_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]'),
        (-3, 4, 0, 'air'),
        (-3, 4, -1, 'polished_andesite_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]'),
        (-3, 4, -2, 'polished_andesite'),
        (-3, 4, -3, 'polished_andesite'),
        (-3, 4, -4, 'polished_andesite'),
        (-3, 4, -5, 'polished_andesite_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]'),
        (-3, 4, -6, 'air'),
        (-4, 0, 0, 'air'),
        (-4, 0, -1, 'oak_planks'),
        (-4, 0, -2, 'air'),
        (-4, 0, -3, 'air'),
        (-4, 0, -4, 'air'),
        (-4, 0, -5, 'oak_planks'),
        (-4, 0, -6, 'air'),
        (-4, 1, 0, 'air'),
        (-4, 1, -1, 'glass'),
        (-4, 1, -2, 'air'),
        (-4, 1, -3, 'air'),
        (-4, 1, -4, 'air'),
        (-4, 1, -5, 'glass'),
        (-4, 1, -6, 'air'),
        (-4, 2, 0, 'air'),
        (-4, 2, -1, 'oak_planks'),
        (-4, 2, -2, 'air'),
        (-4, 2, -3, 'air'),
        (-4, 2, -4, 'air'),
        (-4, 2, -5, 'oak_planks'),
        (-4, 2, -6, 'air'),
        (-4, 3, 0, 'polished_andesite_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]'),
        (-4, 3, -1, 'cobblestone'),
        (-4, 3, -2, 'air'),
        (-4, 3, -3, 'air'),
        (-4, 3, -4, 'air'),
        (-4, 3, -5, 'cobblestone'),
        (-4, 3, -6, 'polished_andesite_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]'),
        (-4, 4, 0, 'air'),
        (-4, 4, -1, 'polished_andesite_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]'),
        (-4, 4, -2, 'polished_andesite'),
        (-4, 4, -3, 'polished_andesite'),
        (-4, 4, -4, 'polished_andesite'),
        (-4, 4, -5, 'polished_andesite_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]'),
        (-4, 4, -6, 'air'),
        (-5, 0, 0, 'air'),
        (-5, 0, -1, 'oak_log[axis=y]'),
        (-5, 0, -2, 'oak_planks'),
        (-5, 0, -3, 'oak_planks'),
        (-5, 0, -4, 'oak_planks'),
        (-5, 0, -5, 'oak_log[axis=y]'),
        (-5, 0, -6, 'air'),
        (-5, 1, 0, 'air'),
        (-5, 1, -1, 'oak_log[axis=y]'),
        (-5, 1, -2, 'glass'),
        (-5, 1, -3, 'glass'),
        (-5, 1, -4, 'glass'),
        (-5, 1, -5, 'oak_log[axis=y]'),
        (-5, 1, -6, 'air'),
        (-5, 2, 0, 'air'),
        (-5, 2, -1, 'oak_log[axis=y]'),
        (-5, 2, -2, 'oak_planks'),
        (-5, 2, -3, 'oak_planks'),
        (-5, 2, -4, 'oak_planks'),
        (-5, 2, -5, 'oak_log[axis=y]'),
        (-5, 2, -6, 'air'),
        (-5, 3, 0, 'polished_andesite_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]'),
        (-5, 3, -1, 'oak_log[axis=y]'),
        (-5, 3, -2, 'cobblestone'),
        (-5, 3, -3, 'cobblestone'),
        (-5, 3, -4, 'cobblestone'),
        (-5, 3, -5, 'oak_log[axis=y]'),
        (-5, 3, -6, 'polished_andesite_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]'),
        (-5, 4, 0, 'air'),
        (-5, 4, -1, 'polished_andesite_stairs[facing=north,half=bottom,shape=outer_right,waterlogged=false]'),
        (-5, 4, -2, 'polished_andesite_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]'),
        (-5, 4, -3, 'polished_andesite_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]'),
        (-5, 4, -4, 'polished_andesite_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]'),
        (-5, 4, -5, 'polished_andesite_stairs[facing=east,half=bottom,shape=outer_right,waterlogged=false]'),
        (-5, 4, -6, 'air'),
        (-6, 0, 0, 'air'),
        (-6, 0, -1, 'air'),
        (-6, 0, -2, 'air'),
        (-6, 0, -3, 'air'),
        (-6, 0, -4, 'air'),
        (-6, 0, -5, 'air'),
        (-6, 0, -6, 'air'),
        (-6, 1, 0, 'air'),
        (-6, 1, -1, 'air'),
        (-6, 1, -2, 'air'),
        (-6, 1, -3, 'air'),
        (-6, 1, -4, 'air'),
        (-6, 1, -5, 'air'),
        (-6, 1, -6, 'air'),
        (-6, 2, 0, 'air'),
        (-6, 2, -1, 'air'),
        (-6, 2, -2, 'air'),
        (-6, 2, -3, 'air'),
        (-6, 2, -4, 'air'),
        (-6, 2, -5, 'air'),
        (-6, 2, -6, 'air'),
        (-6, 3, 0, 'polished_andesite_stairs[facing=north,half=bottom,shape=outer_right,waterlogged=false]'),
        (-6, 3, -1, 'polished_andesite_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]'),
        (-6, 3, -2, 'polished_andesite_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]'),
        (-6, 3, -3, 'polished_andesite_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]'),
        (-6, 3, -4, 'polished_andesite_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]'),
        (-6, 3, -5, 'polished_andesite_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]'),
        (-6, 3, -6, 'polished_andesite_stairs[facing=east,half=bottom,shape=outer_right,waterlogged=false]'),
        (-6, 4, 0, 'air'),
        (-6, 4, -1, 'air'),
        (-6, 4, -2, 'air'),
        (-6, 4, -3, 'air'),
        (-6, 4, -4, 'air'),
        (-6, 4, -5, 'air'),
        (-6, 4, -6, 'diamond_block')]

    for rel_x, rel_y, rel_z, block_name in structure:
        x = start_coordinate.x + rel_x
        y = start_coordinate.y + rel_y
        z = start_coordinate.z + rel_z
        editor.placeBlock((x, y, z), Block(block_name))


"""read_house
arr = [][][]
for x from - to +
    for y from - to +
        for z from - to +
            arr[x][y][z] = getblock(x,y,z)

build_house
for x from - to +
    for y from - to +
        for z from - to +
             placeblock(x,y,z, arr[x][y][z])"""

corner1 = ivec3(-14, 69, 153)
corner2 = ivec3(-20, 73, 147)

print_blocks_in_cube(editor, corner1, corner2)

start = ivec3(-6, 70, 137)

build_house(editor, start)
