from abc import ABC, abstractmethod
from typing import Tuple, List, Callable, Optional


class SemiregularGridInterface(ABC):
    @abstractmethod
    def generate_edges(self, area_range: Tuple[Tuple[float, float],
                                               Tuple[float, float]]) \
            -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """
        Generate a grid covering a rectangular area as a list of edges
        (in order in which they were found).
        The edge is a tuple of two end-points (coordinates [x1, y1] and
        [x2, y2]).

        'Area range' is determined by two vertices - one at the bottom-left
        corner [min_x, min_y] and the other at the top-right corner
        [max_x, max_y].
        """
        pass

    @abstractmethod
    def generate_centres(self, area_range: Tuple[Tuple[float, float],
                                                 Tuple[float, float]]) \
            -> List[Tuple[float, float]]:
        """
        Generate a grid covering a rectangular area as a list of cell centres.
        A cell centre is the centre of the polygon that the grid consists of
        (coordinates [x, y]).

        'Area range' is determined by two vertices - one at the bottom-left
        corner [min_x, min_y] and the other at the top-right corner
        [max_x, max_y].
        """
        pass

    @abstractmethod
    def generate_polygons(self, area_range: Tuple[Tuple[float, float],
                                                  Tuple[float, float]]) \
            -> List[List[Tuple[float, float]]]:
        """
        Generate a grid covering a rectangular area as a list of polygons.
        The polygon is a list of vertices (e.g. for n-gon: coordinates
        [x1, y1], [x2, y2], [x3, y3],... [xn, yn]).

        'Area range' is determined by two vertices - one at the bottom-left
        corner [min_x, min_y] and the other at the top-right corner
        [max_x, max_y].
        """
        pass

    @abstractmethod
    def filter_num_values(self, filter_function: Callable[[float], bool]) \
            -> List[Tuple[int, int, int]]:
        """
        Filter cells based on their numerical values by given 'filter function'
        and return a list of indices of those cells.
        """
        pass

    @abstractmethod
    def filter_rgba_values(self, filter_function: Callable[[
            Tuple[float, float, float, float]], bool]) \
            -> List[Tuple[int, int, int]]:
        """
        Filter cells based on their RGBA values by given 'filter function' and
        return a list of indices of those cells.
        """
        pass

    @abstractmethod
    def index_to_coords(self, index: Tuple[int, int, int]) \
            -> Tuple[float, float]:
        """
        Convert the 'index' of the cell into xy coordinates of the cell's
        centre.
        """
        pass

    @abstractmethod
    def coords_to_index(self, xy: Tuple[float, float]) -> Tuple[int, int, int]:
        """
        Return (i, j, k) index of the cell that contains the given 'xy'
        coordinates.
        """
        pass

    @abstractmethod
    def centre_coords_to_index(self, xy: Tuple[float, float],
                               rdgnt_name: Tuple[int, ...]) -> \
            Tuple[int, int, int]:
        """
        Return (i, j, k) index of the cell whose centre coordinates are 'xy'
        and it is of type 'rdgnt'.
        """
        pass

    @abstractmethod
    def adjacents(self, index: Tuple[int, int, int]) \
            -> List[Tuple[int, int, int]]:
        """
        For a given cell with 'index' (i, j, k), get the indices of the cell's
        adjacents.
        """
        pass

    @abstractmethod
    def delete_values(self, del_rgba: bool = False, del_num: bool = False,
                      keep_indices: Optional[List[Tuple[int, int, int]]] =
                      None) -> None:
        """
        Delete all rgba/numerical values in the grid (except for 'keep indices'
        if specified). If an index with no rgba/numerical value is given,
        it will be ignored.
        """
        pass
