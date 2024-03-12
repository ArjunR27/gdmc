import sys

import numpy as np
from gdpc import __url__, Editor, Block, geometry, Box
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from glm import ivec3


def createFoundations(editor, plots, num_buildings):
    for building_plot in plots[:num_buildings]:
        building_plot.display_info()
        maxHeight = np.max(building_plot.plot)
        minHeight = np.min(building_plot.plot)

        # Calculate corner points of the foundation box
        box_corner1 = (building_plot.x, minHeight, building_plot.z)
        box_corner2 = (building_plot.plot_len, maxHeight - minHeight, building_plot.plot_len)

        # Place hollow box
        geometry.placeBoxHollow(editor, Box(box_corner1, box_corner2), Block("blue_concrete"))
