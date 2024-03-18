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

biomes_dict = biomes_dict = {
    "minecraft:badlands": {"badlands_house.txt"},
    "Bamboo Jungle": {},
    "Beach": {"sand_house.txt"},
    "Birch Forest": {"birch_house.txt"},
    "Cherry Grove": {"cherry_house.txt"},
    "Cold Ocean": {},
    "Dark Forest": {"mushroom_house.txt"},
    "Deep Cold Ocean": {},
    "Deep Dark": {},
    "Deep Frozen Ocean": {},
    "Deep Lukewarm Ocean": {},
    "Deep Ocean": {},
    "Desert": {"sand_house.txt"},
    "Dripstone Caves": {},
    "Eroded Badlands": {"badlands_house.txt"},
    "Flower Forest": {"oak_house.txt"},
    "Forest": {"oak_house.txt"},
    "Frozen Ocean": {},
    "Frozen Peaks": {"igloo.txt"},
    "Frozen River": {},
    "Grove": {"igloo.txt"},
    "Ice Spikes": {},
    "Jagged Peaks": {"igloo.txt"},
    "Jungle": {},
    "Lukewarm Ocean": {},
    "Lush Caves": {},
    "Mangrove Swamp": {"mangrove_house.txt"},
    "Meadow": {"oak_house.txt"},
    "Mushroom Fields": {"mushroom_house.txt"},
    "Ocean": {},
    "Old Growth Birch Forest": {"birch_house.txt"},
    "Old Growth Pine Taiga": {},
    "Old Growth Spruce Taiga": {},
    "Plains": {"oak_house.txt"},
    "River": {"oak_house.txt"},
    "Savanna": {},
    "Savanna Plateau": {},
    "Snowy Beach": {"snowy_beach_house.txt"},
    "Snowy Plains": {"igloo.txt"},
    "Snowy Slopes": {"igloo.txt"},
    "Snowy Taiga": {},
    "Sparse Jungle": {},
    "Stony Peaks": {},
    "Stony Shore": {},
    "Sunflower Plains": {"oak_house.txt"},
    "Swamp": {"swamp_house.txt"},
    "Taiga": {},
    "Warm Ocean": {},
    "Windswept Forest": {},
    "Windswept Gravelly Hills": {},
    "Windswept Hills": {},
    "Windswept Savanna": {},
    "Wooded Badlands": {"wooded_badlands_house.txt"}
}

# Returns the most common biome within the set build area
def check_biome(editor):
    buildArea = editor.getBuildArea()
    return editor.getBiome(buildArea.center)
                

def main():
    editor = Editor()
    maj_biome = check_biome(editor)
    print(maj_biome)
    
if __name__ == "__main__":
    main()


