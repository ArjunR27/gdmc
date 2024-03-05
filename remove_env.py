
import sys
from gdpc import __url__, Editor, Block, geometry, Box
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import *
import numpy as np
import itertools

blocks_to_remove = {
    Block("minecraft:oak_leaves").id,
    Block("minecraft:pine_leaves").id,
    Block("minecraft:birch_leaves").id,
    Block("minecraft:jungle_leaves").id,
    Block("minecraft:acacia_leaves").id,
    Block("minecraft:spruce_leaves").id,
    Block("minecraft:dark_oak_leaves").id,
    Block("minecraft:oak_log").id,
    Block("minecraft:pine_log").id,
    Block("minecraft:birch_log").id,
    Block("minecraft:jungle_log").id,
    Block("minecraft:acacia_log").id,
    Block("minecraft:spruce_log").id,
    Block("minecraft:dark_oak_log").id,
    Block("minecraft:cactus").id,
    Block("minecraft:tall_grass").id,
    Block("minecraft:double_plant").id,
    Block("minecraft:yellow_flower").id,
    Block("minecraft:red_flower").id,
    Block("minecraft:brown_mushroom").id,
    Block("minecraft:red_mushroom").id,
    Block("minecraft:vine").id,
    Block("minecraft:sugar_cane").id,
    Block("minecraft:pumpkin").id,
    Block("minecraft:cocoa").id,
    Block("minecraft:snow_layer").id,
    Block("minecraft:red_concrete").id,
    Block("minecraft:mushroom_stem").id,
}


def remove():
    editor = Editor()
    editor.buffering = True
    editor.bufferLimit = 512
    # editor.multithreading = True
    editor.caching = True
    try:
        editor.checkConnection()
    except InterfaceConnectionError:
        print(
            f"Error: Could not connect to the GDMC HTTP interface at {editor.host}!\n"
            'To use GDPC, you need to use a "backend" that provides the GDMC HTTP interface.\n'
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

    buildRectangle = buildArea.toRect()

    # Create a box of air from the max_surface_height

    worldslice = editor.loadWorldSlice(buildRectangle)
    print("Loaded world slice")

    # heightmap = worldslice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    heightmap = worldslice.heightmaps["WORLD_SURFACE"]

    print("loaded heightmap")

    max_surface_height = np.max(heightmap)
    min_surface_height = np.min(heightmap)


    print(min_surface_height)
    print(max_surface_height)

    points_to_remove = []
    # Use itertools.product() to create combinations of x, y, and z values
    for x, y, z in itertools.product(range(buildArea.begin[0], buildArea.end[0]),
                                      range(min_surface_height, max_surface_height),
                                      range(buildArea.begin[2], buildArea.end[2])):
        block = editor.getBlock((x, y, z))
        if block.id in blocks_to_remove:
            print((x, y, z))
            points_to_remove.append((x, y, z))
    editor.placeBlock(points_to_remove, Block("air"))

def main():
    remove()


if __name__ == "__main__":
    main()
