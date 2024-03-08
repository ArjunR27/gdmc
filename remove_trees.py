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

    worldslice = editor.loadWorldSlice(buildRectangle)
    print("Loaded world slice")

    # heightmap = worldslice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    heightmap = worldslice.heightmaps["WORLD_SURFACE"]

    print("loaded heightmap")

    max_surface_height = np.max(heightmap)
    min_surface_height = np.min(heightmap)
    step = 16
    for x_start in range(0, len(heightmap) + 1, step):
        for z_start in range(0, len(heightmap[0]) + 1, step):
            for block in blocks_to_remove:
                editor.runCommand('fill ' + str(buildArea.begin.x + x_start) + ' ' + str(min_surface_height) + ' ' + str(buildArea.begin.z + z_start) + ' ' + str(buildArea.begin.x + x_start + step-1) + ' ' + str(max_surface_height + 20) + ' ' + str(buildArea.begin.z + z_start + step-1) + ' air replace ' + block)
remove()
