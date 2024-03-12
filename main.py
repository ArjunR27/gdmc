import sys

import numpy as np

from gdpc import __url__, Editor, Block
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import addY

from settler import map_water, find_settlement_location, find_building_locations
from foundationPlacement import createFoundations

# Create an editor object.
# The Editor class provides a high-level interface to interact with the Minecraft world.
editor = Editor()
editor.buffering = True
editor.caching = True

# Check if the editor can connect to the GDMC HTTP interface.
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

# Get the build area.
try:
    buildArea = editor.getBuildArea()
except BuildAreaNotSetError:
    print(
        "Error: failed to get the build area!\n"
        "Make sure to set the build area with the /setbuildarea command in-game.\n"
        "For example: /setbuildarea ~0 0 ~0 ~64 200 ~64"
    )
    sys.exit(1)

print("Loading world slice...")
buildRect = buildArea.toRect()
worldSlice = editor.loadWorldSlice(buildRect)
print("World slice loaded!")

vec = addY(buildRect.center, 30)

heightmap = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

print(f"Heightmap shape: {heightmap.shape}")

print(f"Average height: {int(np.mean(heightmap))}")

begin = buildArea.begin
end = buildArea.end

water_array = map_water(editor, begin, end, heightmap)
settlement_plot, settlement_water, negative, positive = find_settlement_location(begin, water_array, heightmap)
building_plots = find_building_locations(settlement_plot, settlement_water, negative)

num_buildings = 12

createFoundations(editor, building_plots, num_buildings)