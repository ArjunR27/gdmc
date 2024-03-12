import sys
import numpy as np
from gdpc.utils import nonZeroSign
from glm import ivec2, ivec3
import os.path
from gdpc import __url__, Editor, Block
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import addY, dropY
import os
import ast
from settler import BuildingPlot

# The minimum build area size in the XZ-plane
MIN_BUILD_AREA_SIZE = ivec2(35, 35)

# Create an editor object.
editor = Editor()

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

# Check if the build area is large enough in the XZ-plane.
if any(dropY(buildArea.size) < MIN_BUILD_AREA_SIZE):
    print(
        "Error: the build area is too small for this example!\n"
        f"It should be at least {tuple(MIN_BUILD_AREA_SIZE)} blocks large in the XZ-plane."
    )
    sys.exit(1)

# Get a world slice
print("Loading world slice...")
buildRect = buildArea.toRect()
worldSlice = editor.loadWorldSlice(buildRect)
print("World slice loaded!")

editor.buffering = False  # set to false to visualize load

heightmap = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
meanHeight = np.mean(heightmap)
groundCenter = addY(buildRect.center, meanHeight)


class Structure:
    def __init__(self, start, end, filepath, direction, door):
        self.start = start
        self.end = end
        self.filepath = filepath
        self.direction = direction
        self.door = door


def write_schematic_to_file(filename, corner1, corner2):
    """
    iterates through 3D space given by corners and writes them into schematic txt file
    corners are automatically converted into Southeast bottom, and its opposite corner
        :param filename: name of file to store array
        :param corner1: any given corner of the build, converted to SE, bottom
        :param corner2: opposite of corner 1, converted to NW, top
    """
    # Ensure the Schematics directory exists
    directory = "Schematics"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Adjust the filename to include the directory path
    filepath = os.path.join(directory, filename)

    # corrected corners for any corner pair
    corner1_c = [max(corner1[0], corner2[0]), min(corner1[1], corner2[1]), max(corner1[2], corner2[2])]
    corner2_c = [min(corner1[0], corner2[0]), max(corner1[1], corner2[1]), min(corner1[2], corner2[2])]

    with open(filepath, 'w') as file:
        file.write("[\n")
        for x in range(corner1_c[0], corner2_c[0] + nonZeroSign(corner2_c[0] - corner1_c[0]),
                       nonZeroSign(corner2_c[0] - corner1_c[0])):
            file.write("    [\n")
            for y in range(corner1_c[1], corner2_c[1] + nonZeroSign(corner2_c[1] - corner1_c[1]),
                           nonZeroSign(corner2_c[1] - corner1_c[1])):
                file.write("        [")
                for z in range(corner1_c[2], corner2_c[2] + nonZeroSign(corner2_c[2] - corner1_c[2]),
                               nonZeroSign(corner2_c[2] - corner1_c[2])):
                    vec = ivec3(x, y, z)
                    block = str(editor.getBlock(vec))
                    # Extracting the block name without the minecraft: prefix
                    block_name = block.split(":")[-1]  # Assuming block format is 'minecraft:block_name'
                    file.write(f"'{block_name}', ")
                file.write("],\n")
            file.write("    ],\n")
        file.write("]\n")
    print(f"Schematic written to {filepath}")


def read_schematic_from_file(filename):
    """
    Reads schematic from file and returns it as a 3D numpy array representation of the blocks
    :param filename: name of file for which schematic you want to load
    :return numpy array:
    """
    with open(filename, 'r') as file:
        content = file.read()

    # Use ast.literal_eval to safely evaluate the string representation of the array
    schematic_list = ast.literal_eval(content)

    # Convert the nested lists to a NumPy array
    schematic_array = np.array(schematic_list, dtype=object)

    return schematic_array


def build_structure(editor, filepath, plot: BuildingPlot, direction="east"):
    """
    Reads schematic from file and builds structure into world. Structure builds in an order depending
    on which coordinates are used to create the schematic. End result is not affected.
    :param editor: editor instance
    :param filepath: name of file for which schematic you want to load
    :param plot: BuildingPlot, converted to ivec3, the Southeast (pos x, pos z) corner of the plot
    :param direction: String, direction building faces. East is default
    :return numpy array:
    """

    schematic = read_schematic_from_file(filepath)
    door_found = False  # records first door found
    door = None

    # update rotation of structs and rotation mapping for blocks
    if direction == "south":
        schematic = np.rot90(schematic, axes=(0, 2))
        facing_mapping = {"north": "east", "west": "north", "south": "west", "east": "south"}
    if direction == "west":
        schematic = np.flip(schematic, 0)
        facing_mapping = {"north": "north", "west": "east", "south": "south", "east": "west"}
    if direction == "north":
        schematic = np.rot90(schematic, k=-1, axes=(0, 2))
        facing_mapping = {"north": "west", "west": "south", "south": "east", "east": "north"}

    # converts plot to SE start coordinate
    start = ivec3((plot.x + plot.plot_len - 1), plot.y, (plot.z + plot.plot_len - 1))

    x = start[0]
    y = start[1]
    z = start[2]
    end = start
    # print("Start at,", start)

    # builds structure in layers pos to neg X, each layer is built in rows from bottom to top, rows built pos to neg Z
    for layer in schematic:
        for row in layer:
            for block in row:
                if block == "air":  # skips to next block if air
                    end = ivec3(x, y, z)  # keeps track of current latest placed block
                    z = z - 1
                    continue

                # Extract block information
                block_info = block.split('[')
                block_name = block_info[0]
                # print(block) # debug
                block_properties = '[' + block_info[1] if len(block_info) > 1 else ''

                if not door_found and "_door" in block_name:  # finds door for road generation
                    # print(f"Found door: {block},    coordinates", x, y, z) # debug
                    door = ivec3(x, y - 1, z)  # pathing algorithm needs block beneath the door
                    door_found = True

                # Handle rotation of directional blocks
                if direction != "east" and 'facing=' in block_properties:
                    # Extract current facing direction and update properties
                    facing_info = block_properties.split('facing=')[1].split(',')[0]
                    facing_direction = facing_info.replace("]", "").replace("'", "").strip()
                    updated_facing = facing_mapping.get(facing_direction, facing_direction)
                    block_properties = '[' + 'facing=' + updated_facing + ',' + block_properties.split(',', 1)[1]

                # Place the block with the updated information
                editor.placeBlock(ivec3(x, y, z), Block(block_name + block_properties))
                # print("placed", str(block_name + block_properties), "at ", x, y, z)  # debug

                z = z - 1  # moves to next block in row
            z = start[2]  # resets block
            y = y + 1  # moves to next row in layer
        y = start[1]  # resets row
        x = x - 1  # moves to next layer in structure

    # print("End at,", end)
    struct = Structure(start, end, filepath, direction, door)
    return struct


# corner1 = ivec3(-14, 69, 147)
# corner2 = ivec3(-20, 73, 153)
# write_schematic_to_file("basic_house.txt", corner1, corner2)
#
# start = ivec3(-6, 70, 137)
#
# house1 = build_structure(editor, "./Schematics/basic_house.txt", start, "west")
