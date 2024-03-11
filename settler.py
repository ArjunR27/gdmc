#!/usr/bin/env python3

"""
Load and use a world slice.
"""

import sys

import numpy as np

from gdpc import __url__, Editor, Block
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import addY
from tqdm import tqdm


class BuildingPlot:
    def __init__(self, plot, x, z, std):
        self.plot = np.array(plot)
        self.x = x
        self.z = z
        self.std = std
        self.plot_len = len(self.plot)

    def display_info(self):
        print("Building Plot Information:")
        print("Plot Array:")
        print(self.plot)
        print("X:", self.x, self.x + self.plot_len)
        print("Z:", self.z, self.z + self.plot_len)
        print("Standard Deviation:", self.std)

    def get_x_range(self, padding=0):
        return range(self.x - padding, self.x + self.plot_len + padding)

    def get_z_range(self, padding=0):
        return range(self.z - padding, self.z + self.plot_len + padding)

    def __lt__(self, other):
        return self.std < other.std


def check_overlap(plot1, plot2, padding=0):
    x_range1 = plot1.get_x_range(padding)
    z_range1 = plot1.get_z_range(padding)
    x_range2 = plot2.get_x_range(padding)
    z_range2 = plot2.get_z_range(padding)

    # Check for overlap in x and z coordinates
    overlap_x = any(x in x_range1 for x in x_range2) or any(x in x_range2 for x in x_range1)
    overlap_z = any(z in z_range1 for z in z_range2) or any(z in z_range2 for z in z_range1)

    return overlap_x and overlap_z


def filter_overlapping_plots(building_plots, padding):
    filtered_plots = []

    for current_plot in building_plots:
        # Check if current_plot overlaps with any plot in filtered_plots
        if not any(check_overlap(current_plot, previous_plot, padding) for previous_plot in filtered_plots):
            filtered_plots.append(current_plot)

    return filtered_plots


def build_outline(negative_corner, positive_corner, block, y):

    # Place outline
    for x in range(negative_corner[0], positive_corner[0]):
        coord1 = (x, y, negative_corner[2])
        coord2 = (x, y, positive_corner[2])
        editor.placeBlock(coord1, Block(block))
        editor.placeBlock(coord2, Block(block))

    for z in range(negative_corner[2], positive_corner[2]):
        coord1 = (negative_corner[0], y, z)
        coord2 = (positive_corner[0], y, z)
        editor.placeBlock(coord1, Block(block))
        editor.placeBlock(coord2, Block(block))

    # Place corners
    editor.placeBlock(negative_corner, Block("red_concrete"))
    editor.placeBlock(positive_corner, Block("blue_concrete"))


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

localCenter = buildRect.size // 2

centerHeight = heightmap[tuple(localCenter)]
centerTopBlock = worldSlice.getBlock(addY(localCenter, centerHeight - 1))
print(f"Top block at the center of the build area: {centerTopBlock}")

print(f"Average height: {int(np.mean(heightmap))}")

begin = buildArea.begin
end = buildArea.end


def map_water(begin, end, heightmap):
    # Create an array of zeroes with the same dimensions as heightmap
    water_array = np.zeros_like(heightmap)

    # Loop over every 3 rows to estimate water percentage
    total_iterations = (end.x - begin.x) // 3
    for x in tqdm(range(begin.x, end.x, 3), total=total_iterations):
        for z in range(begin.z, end.z):

            # Get top block
            block = editor.getBlock((x, heightmap[x - begin.x, z - begin.z] - 1, z))

            # Set a location to 1 if top block is water
            if "water" in str(block):
                water_array[(x - begin.x)][(z - begin.z)] = 1

    return water_array


def find_settlement_location(begin, water_array, heightmap):
    # Variable declaration
    best_plot = []
    best_plot_water = []
    lowest_std = sys.maxsize

    # Hyperparameters
    plot_size = 50
    step = 1
    max_water_percentage = .3

    # Iterate over building area with step and search for plots
    for x_offset in range(0, len(heightmap) - plot_size + 1, step):
        for z_offset in range(0, len(heightmap[0]) - plot_size + 1, step):

            # Extract a potential plot, get std and water_percentage
            plot = heightmap[x_offset: x_offset + plot_size, z_offset: z_offset + plot_size]
            std = np.std(plot)
            water_plot = water_array[x_offset: x_offset + plot_size, z_offset: z_offset + plot_size]
            water_percentage = 3 * np.count_nonzero(water_plot == 1) / water_plot.size * 100

            # If there is a new lowest std and acceptable water percentage, new best plot found
            if std < lowest_std and water_percentage < max_water_percentage:
                lowest_std = std
                best_plot = BuildingPlot(plot, begin.x + x_offset, begin.z + z_offset, std)
                best_plot_water = water_plot

    # Define corners for new plot
    y = 150
    negative = (best_plot.x, y, best_plot.z)
    positive = (best_plot.x + plot_size, y, best_plot.z + plot_size)

    return best_plot, best_plot_water, negative, positive


def find_building_locations(settlement_plot, settlement_water, negative):
    # Variable declaration
    building_plots = []

    # Hyperparameters
    building_size = 5
    step = 1

    # Iterate over building area with step and search for plots
    for x_offset in range(0, settlement_plot.plot_len - building_size + 1, step):
        for z_offset in range(0, settlement_plot.plot_len - building_size + 1, step):

            # Extract a potential plot, get std and water_percentage
            plot = settlement_plot.plot[x_offset: x_offset + building_size, z_offset: z_offset + building_size]
            std = np.std(plot)
            water_plot = settlement_water[x_offset: x_offset + building_size, z_offset: z_offset + building_size]
            water_percentage = np.count_nonzero(water_plot == 1) / water_plot.size * 100

            # If there is no water
            if water_percentage == 0:
                new_plot = BuildingPlot(plot, negative[0] + x_offset, negative[2] + z_offset, std)
                building_plots.append(new_plot)

    # Sort plots by standard deviation and filter overlapping plots
    padding = 3
    building_plots = sorted(building_plots)
    building_plots = filter_overlapping_plots(building_plots, padding)

    return building_plots


def place_outlines(building_plots, negative, positive):
    # Outline building plot at y level set below
    diamond = "diamond_block"
    gold = "gold_block"

    y = 150

    build_outline(negative, positive, diamond, y)

    for plot in building_plots[:8]:
        negative_corner = (plot.x, y, plot.z)
        positive_corner = (plot.x + plot.plot_len, y, plot.z + plot.plot_len)
        build_outline(negative_corner, positive_corner, gold, y)


water_array = map_water(begin, end, heightmap)
settlement_plot, settlement_water, negative, positive = find_settlement_location(begin, water_array, heightmap)
building_plots = find_building_locations(settlement_plot, settlement_water, negative)

for building_plot in building_plots:
    building_plot.display_info()

place_outlines(building_plots, negative, positive)
