import sys

import numpy as np
from gdpc import __url__, Editor, Block, geometry, Box
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from glm import ivec3

# Create an editor object.
# The Editor class provides a high-level interface to interact with the Minecraft world.
editor = Editor()

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

buildRect = buildArea.toRect()


def createFoundation(buildRectangle):
    worldSlice = editor.loadWorldSlice(buildRectangle)
    print("World slice loaded!")

    heightmap = worldSlice.heightmaps["WORLD_SURFACE"]

    maxHeight = np.max(heightmap)
    minHeight = np.min(heightmap)
    geometry.placeBoxHollow(editor, Box((buildRect.begin.x, minHeight, buildRect.begin.y),
                                        (buildRect.size.x, maxHeight - minHeight, buildRect.size.y)),
                            Block("blue_concrete"))


def createFoundation(x, z, length):
    worldSlice = editor.loadWorldSlice(buildRectangle)
    print("World slice loaded!")

    heightmap = worldSlice.heightmaps["WORLD_SURFACE"]

    maxHeight = np.max(heightmap)
    minHeight = np.min(heightmap)
    geometry.placeBoxHollow(editor, Box((buildRect.begin.x, minHeight, buildRect.begin.y),
                                        (buildRect.size.x, maxHeight - minHeight, buildRect.size.y)),
                            Block("blue_concrete"))
