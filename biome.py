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
def check_biome(editor):
    buildArea = editor.getBuildArea()
    return editor.getBiome(buildArea.center)