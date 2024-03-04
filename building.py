
class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y and self.z == other.z:
            return True
        return False

class Building:
    def __init__(self, length, width, height, corner): #style/texture?
        self.length = length
        self.width = width
        self.height = height
        self.corner = corner
        self.door = Point(corner.x + length//2, corner.y, corner.z)
