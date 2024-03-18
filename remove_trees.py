import sys
from gdpc import __url__, Editor, Block, geometry, Box
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import *
import numpy as np
import itertools

# Dictionary of all target blocks to remove
blocks_to_remove = {
    Block("minecraft:oak_leaves").id,
    Block("minecraft:birch_leaves").id,
    Block("minecraft:jungle_leaves").id,
    Block("minecraft:acacia_leaves").id,
    Block("minecraft:spruce_leaves").id,
    Block("minecraft:dark_oak_leaves").id,
    Block("minecraft:oak_log").id,
    Block("minecraft:birch_log").id,
    Block("minecraft:jungle_log").id,
    Block("minecraft:acacia_log").id,
    Block("minecraft:spruce_log").id,
    Block("minecraft:dark_oak_log").id,
    Block("minecraft:cactus").id,
    Block("minecraft:tall_grass").id,
    Block("minecraft:grass").id, 
    Block("minecraft:dandelion").id, 
    Block("minecraft:azure_bluet").id,
    Block("minecraft:oxeye_daisy").id,
    Block("minecraft:white_tulip").id,
    Block("minecraft:orange_tulip").id,
    Block("minecraft:pink_tulip").id,
    Block("minecraft:red_tulip").id,
    Block("minecraft:lilac").id,
    Block("minecraft:rose_bush").id,
    Block("minecraft:sugar_cane").id,
    Block("minecraft:brown_mushroom").id,
    Block("minecraft:red_mushroom").id,
    Block("minecraft:vine").id,
    Block("minecraft:sugar_cane").id,
    Block("minecraft:pumpkin").id,
    Block("minecraft:cocoa").id,
    Block("minecraft:mushroom_stem").id,
}


# Function to remove target blocks
def remove(editor, buildArea):

    buildRectangle = buildArea.toRect()

    worldslice = editor.loadWorldSlice(buildRectangle)

    heightmap = worldslice.heightmaps["WORLD_SURFACE"]

    #Find highest y level in build area
    max_surface_height = np.max(heightmap)
    #Find lowest y level in build area
    min_surface_height = np.min(heightmap)
    #Step is the size of area to clear at once (16X16)
    step = 16
    #Loop through X and Z ranges
    for x_start in range(0, len(heightmap) + 1, step):
        for z_start in range(0, len(heightmap[0]) + 1, step):
            #Loop through all blocks that we want removed
            for block in blocks_to_remove:
                #Run minecraft command to replace tree blocks
                editor.runCommand('fill ' + str(buildArea.begin.x + x_start) + ' ' + str(min_surface_height) + ' ' + str(buildArea.begin.z + z_start) + ' ' + str(buildArea.begin.x + x_start + step-1) + ' ' + str(max_surface_height + 20) + ' ' + str(buildArea.begin.z + z_start + step-1) + ' air replace ' + block)



