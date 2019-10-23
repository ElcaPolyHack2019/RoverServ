import math


class GpsPosition:
    def __init__(self, id: int, x, y, orientation):
        self.id = id
        self.x = x
        self.y = y
        self.orientation = orientation
        self.orientation_rad = math.radians(orientation)
