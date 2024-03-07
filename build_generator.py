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
import ast

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

# def loopArea(begin: Vec3iLike, end: Optional[Vec3iLike] = None):
#     """Yields all points between <begin> and <end> (end-inclusive).
#     If <end> is not given, yields all points between (0,0,0) and <begin>."""
#     if end is None:
#         begin, end = (0, 0, 0), begin
#
#     for x in range(begin[0], end[0] + nonZeroSign(end[0] - begin[0]), nonZeroSign(end[0] - begin[0])):
#         for y in range(begin[1], end[1] + nonZeroSign(end[1] - begin[1]), nonZeroSign(end[1] - begin[1])):
#             for z in range(begin[2], end[2] + nonZeroSign(end[2] - begin[2]), nonZeroSign(end[2] - begin[2])):
#                 yield ivec3(x, y, z)


import os


def write_structure_to_file(filename, corner1, corner2):
    # Ensure the Schematics directory exists
    directory = "Schematics"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Adjust the filename to include the directory path
    filepath = os.path.join(directory, filename)

    corner1_c = [max(corner1[0], corner2[0]), min(corner1[1], corner2[1]), max(corner1[2], corner2[2])]
    corner2_c = [min(corner1[0], corner2[0]), max(corner1[1], corner2[1]), min(corner1[2], corner2[2])]

    with open(filepath, 'w') as file:
        file.write("[\n")
        for x in range(corner1_c[0], corner2_c[0] + nonZeroSign(corner2_c[0] - corner1_c[0]),
                       nonZeroSign(corner2_c[0] - corner1_c[0])):
            file.write("    [\n")
            for y in range(corner1_c[1], corner2_c[1] + nonZeroSign(corner2_c[1] - corner1_c[1]),
                           nonZeroSign(corner2_c[1] - corner1_c[1])):
                file.write("        [")
                for z in range(corner1_c[2], corner2_c[2] + nonZeroSign(corner2_c[2] - corner1_c[2]),
                               nonZeroSign(corner2_c[2] - corner1_c[2])):
                    vec = ivec3(x, y, z)
                    block = str(editor.getBlock(vec))
                    # Extracting the block name without the minecraft: prefix
                    block_name = block.split(":")[-1]  # Assuming block format is 'minecraft:block_name'
                    file.write(f"'{block_name}', ")
                file.write("],\n")
            file.write("    ],\n")
        file.write("]\n")
    print(f"Structure written to {filepath}")


def read_structure_from_file(filename):
    with open(filename, 'r') as file:
        content = file.read()

    # Use ast.literal_eval to safely evaluate the string representation of the array
    structure_list = ast.literal_eval(content)

    # Convert the nested lists to a NumPy array
    structure_array = np.array(structure_list, dtype=object)

    return structure_array


def build_house(editor, filepath, start, direction="east"):
    structure = read_structure_from_file(filepath)

    # update rotation of structs and rotation mapping for blocks
    if direction == "south":
        structure = np.rot90(structure, axes=(0, 2))
        facing_mapping = {"north": "east", "west": "north", "south": "west", "east": "south"}
    if direction == "west":
        structure = np.flip(structure, 0)
        facing_mapping = {"north": "north", "west": "east", "south": "south", "east": "west"}
    if direction == "north":
        structure = np.rot90(structure, k=-1, axes=(0, 2))
        facing_mapping = {"north": "west", "west": "south", "south": "east", "east": "north"}

    # initial coords

    x = start[0]
    y = start[1]
    z = start[2]

    # builds structure in layers pos to neg X, each layer is built in rows from bottom to top, rows built pos to neg Z
    for layer in structure:
        for row in layer:
            for block in row:
                if block == "air":  # skips to next block if air
                    z = z - 1
                    continue
                # Extract block information
                block_info = block.split('[')
                block_name = block_info[0]
                print(block_name)
                block_properties = '[' + block_info[1] if len(block_info) > 1 else ''

                # Handle rotation of directional blocks
                if direction != "east" and 'facing=' in block_properties:
                    # Extract current facing direction and update properties
                    facing_info = block_properties.split('facing=')[1].split(',')[0]
                    facing_direction = facing_info.replace("]", "").replace("'", "").strip()
                    updated_facing = facing_mapping.get(facing_direction, facing_direction)
                    block_properties = '[' + 'facing=' + updated_facing + ',' + block_properties.split(',', 1)[1]

                # Place the block with the updated information
                editor.placeBlock(ivec3(x, y, z), Block(block_name + block_properties))
                print("placed", str(block_name + block_properties), "at ", x, y, z)
                z = z - 1  # moves to next block in row
            z = start[2]  # resets block
            y = y + 1  # moves to next row in layer
        y = start[1]  # resets row
        x = x - 1  # moves to next layer in structure


# corner1 = ivec3(-14, 69, 153)
# corner2 = ivec3(-20, 73, 147)

corner1 = ivec3(-14, 69, 147)
corner2 = ivec3(-20, 73, 153)

start = ivec3(-6, 70, 137)

write_structure_to_file("basic_house.txt", corner1, corner2)
build_house(editor, "./Schematics/basic_house.txt", start, "south")
