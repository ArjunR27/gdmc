""" 
Analyze the biome that the build area is currently in, this can be used to adapt our builds 
to the current biome/environment.
"""

import sys
from gdpc import Editor
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError  
from gdpc.vector_tools import addY
from collections import Counter
import operator

def check_biome():
    editor = Editor()
    
    try:
        buildArea = editor.getBuildArea()
    except BuildAreaNotSetError:
        print("Failed to get build area")
        sys.exit(1)
    

    buildRect = buildArea.toRect()
    worldSlice = editor.loadWorldSlice(buildRect)


    biome_counter = {}

    print(buildArea)


    for x in range(buildArea.begin[0], buildArea.end[0]):
        for z in range(buildArea.begin[1], buildArea.end[1]):
            for y in range(buildArea.begin[2], buildArea.end[2]):
                biome = worldSlice.getBiome(addY((x,0,z), y))
                if biome != '':
                    if biome not in biome_counter:
                        biome_counter[biome] = 0
                    else:
                        biome_counter[biome] += 1

    
    
    majority_biome = max(biome_counter.items(), key = operator.itemgetter(1))[0]

    print(f"Majority biome in the build area: {majority_biome}")



    """
    localCenter = buildRect.size // 2
    heightmap = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

    center_biome = worldSlice.getBiome(addY(localCenter, 0))

    print(f"Biome at the center of the build area: {center_biome}")
    """

def main():
    check_biome()

if __name__ == "__main__":
    main()

    