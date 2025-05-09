from typing import Tuple, List
import math

from semigrid.gridpolygon import GridPolygon


class DualGraphNode:
    """
    Class representing centers of the polygons (cells) that are tessellating
    the grid = nodes of the dual graph of the grid.

    Each node (=center of the n-gon) has a coordinates, state and type.
    """

    def __init__(self, coordinates: Tuple[float, float],
                 rdgnt_name: Tuple[int, ...]) -> None:
        """
        * coordinates - coordinates of the center
        * rdgnt_name - code representing the type of the node
                            -> RotatedDualGraphNodeType
        * finished - is the search on this node finished
        """
        self._coords = coordinates
        self._rdgnt_name = rdgnt_name
        self._fully_explored = False

    def mark_as_explored(self) -> None:
        self._fully_explored = True

    @property
    def is_fully_explored(self) -> int:
        return self._fully_explored

    @property
    def coords(self) -> Tuple[float, float]:
        return self._coords

    @property
    def rdgnt_name(self) -> Tuple[int, ...]:
        return self._rdgnt_name


class DualGraphNodeType:
    """
    Types of nodes in the dual graph of the grid
    (= possible types of DualGraphNodes).
    """

    def __init__(self,
                 n_polygon: int,
                 neighbour_n_polygons: Tuple[int, ...],
                 edge_size: int,
                 grid_rotation: float = 0) -> None:
        self.polygon = GridPolygon(n_polygon, edge_size)
        self.grid_rotation = grid_rotation  # in radians
        self.edge_size = edge_size
        self._adjacents = [GridPolygon(
            n, edge_size) for n in neighbour_n_polygons]


class RotatedDualGraphNodeType(DualGraphNodeType):
    """
    Rotated DualGraphNodeTypes (DGNT = types of nodes in dual graph of the
    grid) by a given angle in degrees.

    Each type can be uniquely represented by a 'code' -> a tuple:
        (n of polygon in the middle, n of neighbour1, n of neighbour2,...,
                                rotation in degrees of DualGraphNodeType).
    """
    def __init__(self,
                 n_polygon: int,
                 neighbour_n_polygons: Tuple[int, ...],
                 edge_size: int,
                 grid_rotation: float = 0,
                 dgnt_rotation: int = 0) -> None:
        super().__init__(
            n_polygon, neighbour_n_polygons, edge_size, grid_rotation)
        self.dgnt_rotation = dgnt_rotation  # in degrees
        self.rdgnt_name = (n_polygon, *neighbour_n_polygons, dgnt_rotation)
        self.adjacent_centers_coords = self._adjacent_centers_coords()

        # no grid rotation, just in 'constants_script.py'
        self.adjacents_n_rotations = self._calculate_adjacents_n_rotations()
        self.polygon_rotation = self._calculate_polygon_rotation()

    def _adjacent_centers_coords(self) -> List[Tuple[float, float]]:
        """Calculate the coordinates of the adjacent centers."""
        adjacents_centers = []
        initial_rotation = math.radians(
            self.dgnt_rotation) + self.grid_rotation

        for adjacent_index, alpha in enumerate([
                self.polygon.central_angle * i + initial_rotation
                for i in range(self.polygon.n)]):  # rename index! diff meaning
            adjacent = self._adjacents[adjacent_index]
            r = math.sqrt(self.polygon.r**2 -
                          (self.edge_size/2)**2) + math.sqrt(
                              adjacent.r**2 - (self.edge_size/2)**2)
            adjacent_center = r * math.cos(alpha), r * math.sin(alpha)
            adjacents_centers.append(adjacent_center)

        return adjacents_centers

    def _calculate_adjacents_n_rotations(self) -> List[float]:
        """Calculate the polygon rotation of each adjacent"""
        adjacents_rotations = []
        initial_rotation = math.radians(self.dgnt_rotation)
        for i in range(self.polygon.n):
            adjacent = self._adjacents[i]

            angle = math.pi - adjacent.central_angle/2 + \
                initial_rotation + i * self.polygon.central_angle
            true_angle = angle % adjacent.central_angle
            adjacents_rotations.append(math.degrees(true_angle))

        return adjacents_rotations

    def _calculate_polygon_rotation(self) -> float:
        """Calculate the polygon rotation of the polygon in the middle"""
        # limited output {45, 22.5, 30,...}
        fraction = self.edge_size / (2 * self.polygon.r)  # == sin(math.pi/n)
        angle = (math.asin(fraction) + math.radians(self.dgnt_rotation)) \
            % self.polygon.central_angle
        # (math.pi/n + radians(dgnt)) % central angle

        return round(math.degrees(angle), 1)  # it is good... there can be 22.5
