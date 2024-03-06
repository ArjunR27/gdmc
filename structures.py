from gdpc import Block, Editor
from gdpc import geometry as geo
from gdpc.editor_tools import *

def build_wooden_house():
    editor = Editor()
    buildArea = centerBuildAreaOnPlayer(editor, (10,10,10))

    # Define the dimensions of the house
    width = 7
    height = 5
    depth = 7

    # Get the starting position for the house (assuming a centered placement)
    start_x = buildArea.center.x - width // 2
    start_y = buildArea.center.y
    start_z = buildArea.center.z - depth // 2

    # Define the materials for the wooden house
    wood_planks = Block("oak_planks")
    wood_log = Block("oak_log")
    glass_pane = Block("glass_pane")
    air = Block("air")
    door = Block("oak_door")

    # Build the wooden house
    # Walls
    geo.placeCuboid(editor, (start_x, start_y, start_z), (start_x + width - 1, start_y + height - 1, start_z + depth - 1), wood_planks)

    # Roof
    for y_offset in range(3):
        geo.placeCuboid(editor, (start_x + y_offset - 1, start_y + height + y_offset, start_z - 1), (start_x + width - y_offset, start_y + height + y_offset, start_z + depth), wood_planks)

    # Door
    editor.placeBlock((start_x + width // 2, start_y + 1, start_z), door)

    # Clear the space inside the house
    geo.placeCuboid(editor, (start_x + 1, start_y + 1, start_z + 1), (start_x + width - 2, start_y + height - 1, start_z + depth - 2), air)

def main():
    try:
        build_wooden_house()
        print("Wooden house built successfully!")
    except KeyboardInterrupt:
        print("Program execution interrupted.")

if __name__ == "__main__":
    main()


