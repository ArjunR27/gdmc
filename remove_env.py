
import sys
from gdpc import Editor, Block
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import *

def remove_environment(editor, buildArea):
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
    Block("minecraft:snow").id,
    Block("minecraft:red_concrete").id,
    Block("minecraft:red_mushroom").id,
    Block("minecraft:brown_mushroom").id,
    Block("minecraft:mushroom_stem").id
}


    count = 0
    for x in range(buildArea.begin[0], buildArea.end[0]):
        for y in range(buildArea.begin[1], buildArea.end[1]):
            for z in range(buildArea.begin[2], buildArea.end[2]):

                # editor.placeBlock((x,y,z), Block("oak_log"))

                block = editor.getBlock((x,y,z))
                # print(block)
                if block.id in blocks_to_remove:
                    print((x,y,z))
                    editor.placeBlock((x,y,z), Block("air"))

    
                
def main():
    editor = Editor()
    buildArea = editor.getBuildArea()
    editor = Editor(buffering=True, multithreading=True)
    editor.bufferLimit = 512
    editor.caching = True
    editor.cacheLimit = 1024

    print(remove_environment(editor, buildArea))
    print("Removed all oak leaves from the surface of the build area")

if __name__ == "__main__":
    main()


    


