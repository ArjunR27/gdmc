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

biomes_dict = {
    "minecraft:badlands": "badlands_house.txt",
    "minecraft:bamboo_jungle": None,
    "minecraft:beach": "sand_house.txt",
    "minecraft:birch_forest": "birch_house.txt",
    "minecraft:cherry_grove": "cherry_house.txt",
    "minecraft:cold_ocean": None,
    "minecraft:dark_forest": "mushroom_house.txt",
    "minecraft:deep_cold_ocean": None,
    "minecraft:deep_dark": None,
    "minecraft:deep_frozen_ocean": None,
    "minecraft:deep_lukewarm_ocean": None,
    "minecraft:deep_ocean": None,
    "minecraft:desert": "sand_house.txt",
    "minecraft:dripstone_caves": None,
    "minecraft:eroded_badlands": "badlands_house.txt",
    "minecraft:flower_forest": "oak_house.txt",
    "minecraft:forest": "oak_house.txt",
    "minecraft:frozen_ocean": None,
    "minecraft:frozen_peaks": "igloo.txt",
    "minecraft:frozen_river": None,
    "minecraft:grove": "igloo.txt",
    "minecraft:ice_spikes": None,
    "minecraft:jagged_peaks": "igloo.txt",
    "minecraft:jungle": None,
    "minecraft:lukewarm_ocean": None,
    "minecraft:lush_caves": None,
    "minecraft:mangrove_swamp": "mangrove_house.txt",
    "minecraft:meadow": "oak_house.txt",
    "minecraft:mushroom_fields": "mushroom_house.txt",
    "minecraft:ocean": None,
    "minecraft:old_growth_birch_forest": "birch_house.txt",
    "minecraft:old_growth_pine_taiga": None,
    "minecraft:old_growth_spruce_taiga": None,
    "minecraft:plains": "oak_house.txt",
    "minecraft:river": "oak_house.txt",
    "minecraft:savanna": None,
    "minecraft:savanna_plateau": None,
    "minecraft:snowy_beach": "snowy_beach_house.txt",
    "minecraft:snowy_plains": "igloo.txt",
    "minecraft:snowy_slopes": "igloo.txt",
    "minecraft:snowy_taiga": None,
    "minecraft:sparse_jungle": None,
    "minecraft:stony_peaks": None,
    "minecraft:stony_shore": None,
    "minecraft:sunflower_plains": "oak_house.txt",
    "minecraft:swamp": "swamp_house.txt",
    "minecraft:taiga": None,
    "minecraft:warm_ocean": None,
    "minecraft:windswept_forest": None,
    "minecraft:windswept_gravelly_hills": None,
    "minecraft:windswept_hills": None,
    "minecraft:windswept_savanna": None,
    "minecraft:wooded_badlands": "wooded_badlands_house.txt"
}

# Returns the most common biome within the set build area
def check_biome(editor):
    buildArea = editor.getBuildArea()
    print(type(buildArea.center), buildArea.center)
    return editor.getBiome(buildArea.center)
                

def main():
    editor = Editor()
    maj_biome = check_biome(editor)
    print(maj_biome)
    
if __name__ == "__main__":
    main()


