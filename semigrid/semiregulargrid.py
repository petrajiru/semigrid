import math
from typing import Tuple, Dict, List, Optional, Literal, Callable, Union, \
    Any, Set
from shapely.geometry import Point as ShapelyPoint, Polygon as ShapelyPolygon
import numpy as np

from semigrid.semiregulargrid_interface import SemiregularGridInterface
from semigrid.gridpolygon import GridPolygon
from semigrid.dualgraphnode import DualGraphNode, RotatedDualGraphNodeType
from semigrid.constants_generated import ADJACENTS_RDGNT
from semigrid.constants import POSSIBLE_RDGNT, \
    UNIT_VECTORS, UNIT_BLOCK_CELLS_OFFSET


AreaRange = Tuple[Tuple[float, float], Tuple[float, float]]


class SemiregularGrid(SemiregularGridInterface):
    """
    Representation of (Semi-)Regular Grid with arbitrary 'size of edges'
    and 'grid rotation' (provided in radians).
    Its type is determined by 'vertex configuration'.
    """
    def __init__(self,
                 vertex_configuration: Literal['3.3.3.3.3.3', '4.4.4.4',
                                               '6.6.6', '3.3.3.3.6',
                                               '3.3.3.4.4', '3.3.4.3.4',
                                               '3.4.6.4', '3.6.3.6',
                                               '3.12.12', '4.6.12', '4.8.8'],
                 edge_size: int = 50,
                 grid_rotation: float = 0) -> None:

        if edge_size < 10:
            raise Exception("Edge size is too short.")
        self._notation = str(vertex_configuration)
        self._vertex_configuration: Tuple[int, ...] = tuple(
            int(n) for n in vertex_configuration.split("."))

        self._edge_size: int = edge_size
        self._grid_rotation: float = grid_rotation
        self._rgba_values: Dict[Tuple[int, int, int],
                                Tuple[float, float, float, float]] = {}
        self._num_values: Dict[Tuple[int, int, int], float] = {}

        # e.g. [(4, 3, 4, 3, 4, 90), (3, 3, 3, 4, 30), (3, 3, 3, 4, 210)]
        self._rdgnt_names = POSSIBLE_RDGNT[self._vertex_configuration]

        # optimalisation
        # {(polygon_n, rotation): [vertices]}
        self._polygons_coords: Dict[Tuple[int, float],
                                    List[Tuple[float, float]]] = {}
        # e.g. {(3, 3, 3, 3, 30): RotatedDualGraphNodeType}
        self._rdgnt_dic = self._build_rdgnt_dic()
        # e.g. {(3, 3, 3, 3, 30): [(3, 3, 3, 3, 90),
        #                          (3, 3, 3, 3, 90), (3, 3, 3, 3, 90)]}
        self._adjacents_rdgnt: Dict[
            Tuple[int, ...], List[Tuple[int, ...]]] = \
            ADJACENTS_RDGNT[self._vertex_configuration]

        # conversion
        self._unit_vectors = self._calculate_unit_vectors()
        self._cells_offsets = self._calculate_cells_offsets()

        self._shapely_polygons_near_origin: Dict[
            Tuple[int, int, int],
            ShapelyPolygon] = self._create_shapely_polygons()

        # search
        self._search_counter: int = 0
        self._discovered_nodes: Dict[Tuple[int, int, int], DualGraphNode] = {}
        self._edges: List[Tuple[Tuple[float, float], Tuple[float, float]]] = []
        self._dual_graph: List[Tuple[Tuple[float, float],
                                     Tuple[float, float]]] = []

    @property
    def notation(self) -> str:
        return self._notation

    @property
    def edge_size(self) -> int:
        return self._edge_size

    @property
    def grid_rotation(self) -> float:
        return self._grid_rotation

    @property
    def rgba_values(self) -> List[Tuple[Tuple[int, int, int],
                                        Tuple[float, float, float, float]]]:
        return [(index, value) for index, value in self._rgba_values.items()]

    @property
    def numerical_values(self) -> List[Tuple[Tuple[int, int, int],
                                             float]]:
        return [(index, value) for index, value in self._num_values.items()]

    @property
    def generated_cells(self) -> Dict[Tuple[int, int, int], DualGraphNode]:
        return self._discovered_nodes

    def _calculate_origin_cells_range(self) -> AreaRange:
        """Calculate the rectangular area around origin that will contain
        the modulo unit vectors."""
        s1, s2 = self._unit_vectors
        vts = [s1, s2, (0, 0), (s1[0] + s2[0], s1[1] + s2[1])]
        min_x = min(vertex[0] for vertex in vts)
        min_y = min(vertex[1] for vertex in vts)
        max_x = max(vertex[0] for vertex in vts)
        max_y = max(vertex[1] for vertex in vts)
        return ((min_x, min_y), (max_x, max_y))

    def _create_shapely_polygons(self) \
            -> Dict[Tuple[int, int, int], ShapelyPolygon]:
        """Create shapely polygons near the origin."""
        pattern_polygons = {}
        near_origin_area = self._calculate_origin_cells_range()

        for i, j in [(i, j) for j in (-1, 0, 1) for i in (-1, 0, 1)]:
            for k in range(len(self._rdgnt_names)):
                coords = self.index_to_coords((i, j, k))
                rdgnt_name = self._rdgnt_names[k]
                rdgnt = self._rdgnt_dic[rdgnt_name]

                if self._is_polygon_visible(coords, rdgnt, near_origin_area):
                    vertices = self._polygon_coords(
                        coords, rdgnt_name[0], rdgnt.polygon_rotation)
                    pattern_polygons[(i, j, k)] = ShapelyPolygon(
                        vertices)

        return pattern_polygons

    def _calculate_cells_offsets(self) \
            -> Dict[Tuple[int, ...], Tuple[float, float]]:
        """Scale and rotate the offsets of the cells in the unit block."""
        cells_offsets = dict(UNIT_BLOCK_CELLS_OFFSET[
            self._vertex_configuration])
        for rdgnt_name, offset in cells_offsets.items():
            cells_offsets[rdgnt_name] = self._scale_and_rotate(offset)

        return cells_offsets

    def _calculate_unit_vectors(self) -> \
            Tuple[Tuple[float, float], Tuple[float, float]]:
        """Scale and rotate unit vectors accordingly."""
        u, v = UNIT_VECTORS[self._vertex_configuration]
        return self._scale_and_rotate(u), self._scale_and_rotate(v)

    def _scale_and_rotate(self, vector: Tuple[float, float]) \
            -> Tuple[float, float]:
        """
        Scale the 'vector' by the edge size and then rotate it by the grid
        rotation.
        """
        x, y = vector
        return self._rotate_vector(x * self._edge_size, y * self._edge_size)

    def _rotate_vector(self, ux: float, uy: float) -> Tuple[float, float]:
        """
        Rotate vector '(ux, uy)' around center by grid rotation and
        return its new coordinates.
        """
        cos_alpha = math.cos(self._grid_rotation)
        sin_alpha = math.sin(self._grid_rotation)
        matrix = np.array([[cos_alpha, -sin_alpha], [sin_alpha, cos_alpha]])
        new_ux, new_uy = np.dot(matrix, np.array([ux, uy]))

        return (round(float(new_ux), 5), round(float(new_uy), 5))

    def _build_rdgnt_dic(self) \
            -> Dict[Tuple[int, ...], RotatedDualGraphNodeType]:
        """
        Build dictionary for better availability
        to the 'RotatedDualGraphNodeType's.
        """
        rdgnt_dic = {}
        for rdgnt_name in self._rdgnt_names:
            rdgnt_dic[rdgnt_name] = \
                RotatedDualGraphNodeType(rdgnt_name[0], rdgnt_name[1:-1],
                                         self._edge_size, self._grid_rotation,
                                         rdgnt_name[-1])

        return rdgnt_dic

    def _move_vertices(self, vector: Tuple[float, float],
                       vertices: List[Tuple[float, float]]) \
            -> List[Tuple[float, float]]:
        """Move 'vertices' by 'vector'."""
        u, v = vector
        return [(x + u, y + v) for x, y in vertices]

    def _adj_centers_coords(self, rdgnt_name: Tuple[int, ...],
                            coords: Tuple[float, float]) \
            -> List[Tuple[float, float]]:
        """
        Get coordinates of the adjacents's centers (of the given polygon's
        center 'coords').
        """
        rdgn = self._rdgnt_dic[rdgnt_name]
        adj_centers_coords_origin = rdgn.adjacent_centers_coords
        return self._move_vertices(coords, adj_centers_coords_origin)

    def _polygon_coords_origin(self, polygon: GridPolygon, alpha: float) \
            -> List[Tuple[float, float]]:
        """
        Return the vertices of a polygon that is rotated by 'alpha'. Center of
        the polygon is at the origin.
        """
        initial_rotation = alpha + self._grid_rotation
        return [(round(polygon.r * math.cos(alpha), 5),
                 round(polygon.r * math.sin(alpha), 5))
                for alpha in (polygon.central_angle * i + initial_rotation
                              for i in range(polygon.n))]

    def _polygon_coords(self, center: Tuple[float, float], n: int,
                        rotation: float) -> List[Tuple[float, float]]:
        """
        Get coordinates of polygon (list of vertices).
        It takes a polygon's 'center' coordinates, its type 'n' and
        its 'rotation' in degrees.
        """
        polygon_coords_origin = self._polygons_coords.get((n, rotation))
        if polygon_coords_origin is None:
            polygon_coords_origin = self._polygon_coords_origin(
                GridPolygon(n, self._edge_size), math.radians(rotation))
            self._polygons_coords[(n, rotation)] = polygon_coords_origin

        polygon_coords = self._move_vertices(center, polygon_coords_origin)
        return [(round(x, 5), round(y, 5)) for x, y in polygon_coords]

    def _polygon_instersects_range(self, polygon: List[Tuple[float, float]],
                                   range: AreaRange) -> bool:
        """Answer whether the polygen is intersecting the 'range'."""
        range_min, range_max = range
        min_x = min(vertex[0] for vertex in polygon)
        min_y = min(vertex[1] for vertex in polygon)
        max_x = max(vertex[0] for vertex in polygon)
        max_y = max(vertex[1] for vertex in polygon)

        return range_min[0] < max_x and min_x < range_max[0] \
            and range_min[1] < max_y and min_y < range_max[1]

    def _vertex_within_range(self, vertex: Tuple[float, float],
                             range: AreaRange) -> bool:
        """Answer whether the vertex is within the range."""
        x, y = vertex
        return range[0][0] < x < range[1][0] and range[0][1] < y < range[1][1]

    def _is_polygon_visible(self, center_coords: Tuple[float, float],
                            rdgnt: RotatedDualGraphNodeType,
                            area_range: AreaRange) -> bool:
        """
        Answer whether the polygon of 'rdgnt' type and center
        having 'center_coords' is visible within the range.
        """
        polygon_coords = self._polygon_coords(center_coords, rdgnt.polygon.n,
                                              rdgnt.polygon_rotation)

        return self._polygon_instersects_range(polygon_coords, area_range)

    def _get_edge(self, i: int, center_rdgnt: RotatedDualGraphNodeType,
                  polygon_vertices: List[Tuple[float, float]]) \
            -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """
        Get coordinates of edge between polygon (of 'rdgnt' type) and its i-th
        adjacent.
        """
        central_angle = math.degrees(center_rdgnt.polygon.central_angle)
        index_a = int(i + center_rdgnt.dgnt_rotation//central_angle)
        index_b = index_a - 1 if center_rdgnt.dgnt_rotation % \
            central_angle < center_rdgnt.polygon_rotation else index_a + 1

        return polygon_vertices[index_b % center_rdgnt.polygon.n], \
            polygon_vertices[index_a % center_rdgnt.polygon.n]

    def _get_adj_rdgnt(self, rdgnt_name: Tuple[int, ...], i: int) -> \
            RotatedDualGraphNodeType:
        """
        Get for the cell (of 'rdgnt' type) the rdgnt of it's 'i-th' adjacent.
        """
        adj_rdgnt_name = self._adjacents_rdgnt[rdgnt_name][i]
        return self._rdgnt_dic[adj_rdgnt_name]

    def _search_adjacents(self, node: DualGraphNode,
                          queue: List[DualGraphNode], area_range: AreaRange,
                          edges: bool = False) -> None:
        """
        Explore the adjacents of the given 'node'.
        If 'edges' is not None, the coordinates of edges discovered during the
        search will be stored.
        """
        node_index = self.center_coords_to_index(node.coords, node.rdgnt_name)
        node_rdgnt = self._rdgnt_dic[node.rdgnt_name]
        if edges:
            polygon_vertices = self._polygon_coords(
                node.coords, node.rdgnt_name[0], node_rdgnt.polygon_rotation)

        for i, adj_node_coords in enumerate(self.adjacents_coords(node_index)):
            self._dual_graph.append((node.coords, adj_node_coords))
            adj_node_index = self.center_coords_to_index(
                adj_node_coords, self._get_adj_rdgnt(
                    node.rdgnt_name, i).rdgnt_name)
            if adj_node_index in self._discovered_nodes:
                if edges and not self._discovered_nodes[adj_node_index
                                                        ].is_fully_explored:
                    self._edges.append(self._get_edge(i, node_rdgnt,
                                                      polygon_vertices))
                continue

            adj_node_rdgnt = self._get_adj_rdgnt(node.rdgnt_name, i)
            if not self._vertex_within_range(adj_node_coords, area_range):
                if not self._is_polygon_visible(adj_node_coords,
                                                adj_node_rdgnt, area_range):
                    continue

            new_node = DualGraphNode(adj_node_coords,
                                     adj_node_rdgnt.rdgnt_name)
            self._discovered_nodes[adj_node_index] = new_node
            queue.append(new_node)

            if edges:
                self._edges.append(self._get_edge(i, node_rdgnt,
                                                  polygon_vertices))

        self._discovered_nodes[node_index].mark_as_explored()

    def _search_area(self, area_range: AreaRange, edges: bool = False) \
            -> None:
        """
        Explore the centers of the polygons in the grid visible within
        the given 'area_range' (= nodes) and store them by their indices.
        If 'edges' is not None, the coordinates of edges discovered during the
        search will be stored.
        """
        self._search_counter += 1
        self._discovered_nodes = {}
        self._dual_graph = []

        min_xy, max_xy = area_range
        if min_xy[0] >= max_xy[0] or min_xy[1] >= max_xy[1]:
            print("Invalid area range", area_range)
            return

        range_midpoint_coords = (max_xy[0] + min_xy[0])/2, \
            (max_xy[1] + min_xy[1])/2
        initial_index = self.coords_to_index(range_midpoint_coords)
        initial_node_coords = self.index_to_coords(initial_index)
        initial_node = DualGraphNode(initial_node_coords,
                                     self._rdgnt_names[initial_index[-1]])
        self._discovered_nodes[initial_index] = initial_node
        queue: List[DualGraphNode] = [initial_node]

        while queue != []:
            node = queue.pop(0)
            self._search_adjacents(node, queue, area_range, edges)

    def generate_edges(self, area_range: AreaRange) \
            -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
        self._edges = []
        self._search_area(area_range, edges=True)
        return self._edges

    def generate_centers(self, area_range: AreaRange) -> \
            List[Tuple[float, float]]:
        self._search_area(area_range)
        return [node.coords for node in self._discovered_nodes.values()]

    def generate_polygons(self, area_range: AreaRange) \
            -> List[List[Tuple[float, float]]]:
        polygons = []
        self._search_area(area_range)
        for node in self._discovered_nodes.values():
            n = node.rdgnt_name[0]
            rotation = self._rdgnt_dic[node.rdgnt_name].polygon_rotation
            polygons.append(self._polygon_coords(node.coords, n, rotation))

        return polygons

    def _coords_to_approx_index(self, xy: Tuple[float, float]) \
            -> Tuple[float, float]:
        """
        Convert coordinates 'xy' into approximate float index ij.
        """
        u, v = self._unit_vectors
        j = (u[0] * xy[1] - xy[0] * u[1])/(u[0] * v[1] - v[0] * u[1])
        i = (xy[0] - j * v[0])/u[0]
        return i, j

    def index_to_coords(self, index: Tuple[int, int, int]) \
            -> Tuple[float, float]:
        i, j, k = index
        u, v = self._unit_vectors
        x = i * u[0] + j * v[0]
        y = i * u[1] + j * v[1]
        rdgnt_name = self._rdgnt_names[k]
        x_offset, y_offset = self._cells_offsets[rdgnt_name]
        return x + x_offset, y + y_offset

    def center_coords_to_index(self, xy: Tuple[float, float],
                               rdgnt_name: Tuple[int, ...]) -> \
            Tuple[int, int, int]:
        if rdgnt_name not in self._rdgnt_names:
            raise Exception("RDGNT name does not exist in this grid")

        x_offset, y_offset = self._cells_offsets[rdgnt_name]
        x = xy[0] - x_offset
        y = xy[1] - y_offset

        u, v = self._unit_vectors
        j = round((u[0] * y - x * u[1])/(u[0] * v[1] - v[0] * u[1]))
        i = round((x - j * v[0])/u[0])
        k = self._rdgnt_names.index(rdgnt_name)

        return i, j, k

    def coords_to_index(self, xy: Tuple[float, float]) -> Tuple[int, int, int]:
        approx_i, approx_j = self._coords_to_approx_index(xy)
        r_i, r_j = math.floor(approx_i), math.floor(approx_j)
        u, v = self._unit_vectors
        near_xy = xy[0] - r_i * u[0] - r_j * v[0], \
            xy[1] - r_i * u[1] - r_j * v[1]

        pnt = ShapelyPoint(near_xy)
        for ijk, pol in self._shapely_polygons_near_origin.items():
            if pol.covers(pnt):
                return ijk[0] + r_i, ijk[1] + r_j, ijk[2]

        print(f"\n{xy} -> {near_xy}\n")
        raise Exception("Conversion 'coordinates' to 'index' failed.")

    def filter_num_values(self, filter_function: Callable[[float], bool]) \
            -> List[Tuple[int, int, int]]:
        return self._filter_values(filter_function, self._num_values)

    def filter_rgba_values(self, filter_function: Callable[[
            Tuple[float, float, float, float]], bool]) \
            -> List[Tuple[int, int, int]]:
        return self._filter_values(filter_function, self._rgba_values)

    def _filter_values(self, filter_func: Union[Callable[[float], bool], Callable[[Tuple[float, float, float,float]],bool]],  # Callable[[Union[Tuple[float, float, float, float], float]], bool],
                       values_dic: Union[Dict[Tuple[int, int, int],
                                   Tuple[float, float, float, float]],
                              Dict[Tuple[int, int, int], float]]) -> \
                                List[Tuple[int, int, int]]:
        """
        Filter cells based on their values by given 'filter function' and
        return a list of indices of those cells.
        """
        filtered_values: Set[
            Union[float, Tuple[float, float, float, float]]] = set(filter(
                filter_func, values_dic.values()))
        return [index for index, value in values_dic.items()
                if value in filtered_values]

    def adjacents_coords(self, index: Tuple[int, int, int]) \
            -> List[Tuple[float, float]]:
        rdgnt_name = self._rdgnt_names[index[2]]
        adjacents_coords = self._adj_centers_coords(
            rdgnt_name, self.index_to_coords(index))

        return adjacents_coords

    def delete_values(self, del_rgba: bool = False,
                      del_num: bool = False,
                      keep_indices: Optional[List[Tuple[
                          int, int, int]]] = None) -> None:
        if del_rgba:
            self._delete_rgba_values(keep_indices)
        if del_num:
            self._delete_num_values(keep_indices)

    def _delete_rgba_values(self, keep_indices: Optional[
            List[Tuple[int, int, int]]] = None) -> None:
        """
        Delete all rgba values in the grid (except for 'keep indices'
        if specified).
        If an index with no rgba value is given, it will be ignored.
        """
        if keep_indices is None:
            self._rgba_values = {}
            return None

        self._rgba_values = {keep_index: self._rgba_values[keep_index]
                             for keep_index in keep_indices
                             if keep_index in self._rgba_values}

    def _delete_num_values(self, keep_indices: Optional[
            List[Tuple[int, int, int]]] = None) -> None:
        """
        Delete all numerical values in the grid (except for 'keep indices'
        if specified).
        If an index with no numerical value is given, it will be ignored.
        """
        if keep_indices is None:
            self._num_values = {}
            return None

        self._num_values = {keep_index: self._num_values[keep_index]
                            for keep_index in keep_indices
                            if keep_index in self._num_values}

    def _describe_type(self, value: Any) \
            -> str:
        if isinstance(value, tuple):
            types = ', '.join(type(v).__name__ for v in value)
            return f"Tuple[{types}]"

        return type(value).__name__

    def __setitem__(self, index: Tuple[int, int, int],
                    value: Union[Tuple[float, float, float, float],
                                 float]) -> None:
        if isinstance(value, tuple) and len(value) == 4 and \
                all(isinstance(item, (float, int)) for item in value):
            self._rgba_values[index] = value
        elif isinstance(value, (float, int)):
            self._num_values[index] = value
        else:
            type_name = self._describe_type(value)
            print(f"\
Invalid value: expected Tuple[float, float, float, float] or float;\
 {type_name} was given")
