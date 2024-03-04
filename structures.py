import sys
import numpy as np
from glm import ivec2, ivec3
from gdpc import __url__, Editor, Block, geometry
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import Y, addY, dropY, line3D, circle, fittingCylinder
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
geometry.placeRectOutline(editor, buildRect, 100, Block("red_concrete"))

heightmap = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
meanHeight = np.mean(heightmap)
groundCenter = addY(buildRect.center, meanHeight)

# Build a floating 5x9 platform in the middle of the build area.
buildRect = buildArea.toRect()
platformRect = buildRect.centeredSubRect((6, 9))
placeBox(editor, platformRect.toBox(100, 1), Block("sandstone"))
placeBox(editor, platformRect.toBox(101, 10), Block("air"))  # Clear some space

wallPalette = [Block(id) for id in 3 * ["stone_bricks"] + ["cobblestone", "polished_andesite"]]

placeCuboid(
    editor,
    addY(platformRect.offset) + ivec3(5, 101, 0),
    addY(platformRect.offset) + ivec3(5, 103, 8),
    wallPalette
)
