import math


class GridPolygon:
    """
    Class representing a polygon (cell) in the grid.
    It stores the polygon characteristics:
    * n = number of sides
    * r = radius
    * central_angle = the angle (in radians) formed at the center of a polygon
        by radii drawn to two adjacent vertices
    """
    def __init__(self, n: int, edge_size: int = 10) -> None:
        self._n = n
        self._r = edge_size/(2*math.sin(math.pi/n))
        self._central_angle = 2 * math.pi/n

    @property
    def n(self) -> int:
        return self._n

    @property
    def r(self) -> float:
        return self._r

    @property
    def central_angle(self) -> float:
        return self._central_angle
