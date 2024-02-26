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


# Returns the most common biome within the set build area
def check_biome():
    editor = Editor()

    try:
        buildArea = editor.getBuildArea()
    except BuildAreaNotSetError:
        print("Failed to get build area")
        sys.exit(1)

    buildRect = buildArea.toRect()
    worldSlice = editor.loadWorldSlice(buildRect)

    biome_counter = Counter()

    
    for x in range(buildArea.begin[0], buildArea.end[0]):
        for z in range(buildArea.begin[1], buildArea.end[1]):
            for y in range(buildArea.begin[2], buildArea.end[2]):
                biome = worldSlice.getBiome(addY((x, 0, z), y))
                if biome:
                    biome_counter[biome] += 1

    majority_biome = biome_counter.most_common(1)[0][0]
    
    return majority_biome


# Get list of blocks for each biome, builds are biome-dependent
def get_block_list():
    return None


def main():
    maj_biome = check_biome()
    print(maj_biome)

if __name__ == "__main__":
    main()

