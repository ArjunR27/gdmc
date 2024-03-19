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
    "minecraft:badlands": "Schematics\\badlands_house.txt",
    "minecraft:bamboo_jungle": "Schematics\\jungle_house.txt",
    "minecraft:beach": "Schematics\\sand_house.txt",
    "minecraft:birch_forest": "Schematics\\birch_house.txt",
    "minecraft:cherry_grove": "Schematics\\cherry_house.txt",
    "minecraft:cold_ocean": None,
    "minecraft:dark_forest": "Schematics\\mushroom_house.txt",
    "minecraft:deep_cold_ocean": None,
    "minecraft:deep_dark": None,
    "minecraft:deep_frozen_ocean": "Schematics\\ice_spike_house.txt",
    "minecraft:deep_lukewarm_ocean": None,
    "minecraft:deep_ocean": None,
    "minecraft:desert": "Schematics\\sand_house.txt",
    "minecraft:dripstone_caves": None,
    "minecraft:eroded_badlands": "Schematics\\badlands_house.txt",
    "minecraft:flower_forest": "Schematics\\oak_house.txt",
    "minecraft:forest": "Schematics\\oak_house.txt",
    "minecraft:frozen_ocean": "Schematics\\ice_spike_house.txt",
    "minecraft:frozen_peaks": "Schematics\\igloo.txt",
    "minecraft:frozen_river": "Schematics\\ice_spike_house.txt",
    "minecraft:grove": "Schematics\\igloo.txt",
    "minecraft:ice_spikes": "Schematics\\ice_spike_house.txt",
    "minecraft:jagged_peaks": "Schematics\\igloo.txt",
    "minecraft:jungle": "Schematics\\jungle_house.txt",
    "minecraft:lukewarm_ocean": None,
    "minecraft:lush_caves": None,
    "minecraft:mangrove_swamp": "Schematics\\mangrove_house.txt",
    "minecraft:meadow": "Schematics\\oak_house.txt",
    "minecraft:mushroom_fields": "Schematics\\mushroom_house.txt",
    "minecraft:ocean": None,
    "minecraft:old_growth_birch_forest": "Schematics\\birch_house.txt",
    "minecraft:old_growth_pine_taiga": "Schematics\\spruce_house.txt",
    "minecraft:old_growth_spruce_taiga": "Schematics\\spruce_house.txt",
    "minecraft:plains": "Schematics\\oak_house.txt",
    "minecraft:river": "Schematics\\oak_house.txt",
    "minecraft:savanna": "Schematics\\acacia_house.txt",
    "minecraft:savanna_plateau": "Schematics\\acacia_house.txt",
    "minecraft:snowy_beach": "Schematics\\snowy_beach_house.txt",
    "minecraft:snowy_plains": "Schematics\\igloo.txt",
    "minecraft:snowy_slopes": "Schematics\\igloo.txt",
    "minecraft:snowy_taiga": "Schematics\\spruce_house.txt",
    "minecraft:sparse_jungle": "Schematics\\jungle_house.txt",
    "minecraft:stony_peaks": "Schematics\\stone_house.txt",
    "minecraft:stony_shore": "Schematics\\stone_house.txt",
    "minecraft:sunflower_plains": "Schematics\\oak_house.txt",
    "minecraft:swamp": "Schematics\\swamp_house.txt",
    "minecraft:taiga": "Schematics\\spruce_house.txt",
    "minecraft:warm_ocean": None,
    "minecraft:windswept_forest": "Schematics\\spruce_house.txt",
    "minecraft:windswept_gravelly_hills": "Schematics\\spruce_house.txt",
    "minecraft:windswept_hills": "Schematics\\spruce_house.txt",
    "minecraft:windswept_savanna": "Schematics\\acacia_house.txt",
    "minecraft:wooded_badlands": "Schematics\\wooded_badlands_house.txt"
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


