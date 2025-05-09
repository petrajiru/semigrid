import sys
import os
from typing import List, Tuple, Dict
import math
from datetime import datetime

from semigrid.dualgraphnode import RotatedDualGraphNodeType
from semigrid.gridpolygon import GridPolygon
from semigrid.constants import POSSIBLE_RDGNT

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..')))

RDGNTName = Tuple[int, ...]


def build_polygontype_dic(vertex_configuration: Tuple[int, ...]) \
        -> Dict[int, GridPolygon]:
    """
    Build dictionary for better avaibility to the 'PolygonType' objects.
    """
    polygon_types = {}
    for n in vertex_configuration:
        if n not in polygon_types:
            polygon_types[n] = GridPolygon(n, 100)

    return polygon_types


def build_rdgnt_dic(rdgn_types_names: List[RDGNTName]) \
        -> Dict[RDGNTName, RotatedDualGraphNodeType]:
    """
    Build dictionary for better avaibility to the 'RotatedDualGraphNodeType's.
    """
    rdgnt_dic = {}
    for rdgnt_name in rdgn_types_names:
        polygon_n = rdgnt_name[0]
        adjacent_polygons_n = rdgnt_name[1:-1]
        dgnt_rotation = rdgnt_name[-1]
        rdgnt_dic[rdgnt_name] = RotatedDualGraphNodeType(polygon_n,
                                                         adjacent_polygons_n,
                                                         100, 0,
                                                         dgnt_rotation)

    return rdgnt_dic


def build_precalculated_rdgnt_dic(rdgn_types_names: List[RDGNTName],
                                  polygon_types: Dict[int, GridPolygon]) ->\
                                    Dict[RDGNTName, List[RDGNTName]]:
    """
    Precalculate in advance for each RotatedDualGridNodeType
    the RotatedDualGridNodeType of theirs neighbours.
    """
    rgnt_dic = build_rdgnt_dic(rdgn_types_names)
    neighbours_types = {}
    for rdgnt_name in rdgn_types_names:
        rdgnt_neighbours_types = []
        neighbours_n = rdgnt_name[1:-1]
        for i, neighbour_n in enumerate(neighbours_n):
            neigbour_type = calculate_dgn_type(neighbour_n,
                                               rdgnt_name, i, rdgn_types_names,
                                               rgnt_dic, polygon_types)
            rdgnt_neighbours_types.append(neigbour_type)

        neighbours_types[rdgnt_name] = rdgnt_neighbours_types

    return neighbours_types


def calculate_dgn_type(polygon_n: int,
                       rdgnt_name: RDGNTName,
                       i: int,
                       possible_types: List[RDGNTName],
                       rdgnt_dic: Dict[RDGNTName, RotatedDualGraphNodeType],
                       polygon_types: Dict[int, GridPolygon]) -> RDGNTName:
    """
    Calculate which RotatedDualGraphNodeType is the 'n_polygon'
    if it is the 'i-th' neighbour of the node which type is 'rdgnt'.
    """
    m = 1
    neighbour_rotation = rdgnt_dic[rdgnt_name].adjacents_n_rotations[i]
    neighbour_rotation = round(neighbour_rotation, ndigits=1)

    # only one possible type in the grid
    if len(possible_types) == 1:
        return possible_types[0]

    # filter types that have 'polygon_n' in the center
    types_starting_with_polygon = [possible_type for possible_type in
                                   possible_types if possible_type[0] ==
                                   polygon_n]
    if len(types_starting_with_polygon) == 1:
        return types_starting_with_polygon[0]

    # filter types which polygon rotation corresponds with the polygon rotation
    # of the neighbour calculated from the rdgnt
    types_with_rotation = [possible_type
                           for possible_type in types_starting_with_polygon
                           if rdgnt_dic[possible_type].polygon_rotation ==
                           neighbour_rotation]
    if len(types_with_rotation) == 1:
        return types_with_rotation[0]

    # filter types that have at certain angle type of rdgnt n polygon
    # in the center
    alpha = math.radians(rdgnt_name[-1]) + \
        i * polygon_types[rdgnt_name[0]].central_angle
    beta = math.pi + alpha
    correct_angle = []
    for possible_type in types_with_rotation:
        j = round((beta - math.radians(possible_type[-1])) /
                  polygon_types[polygon_n].central_angle) % polygon_n
        if possible_type[1 + j] == rdgnt_name[0]:
            correct_angle.append((possible_type, j))
    if len(correct_angle) == 1:
        return correct_angle[0][0]

    previous_n = rdgnt_name[(i - 1) % 3 + 1]
    following_n = rdgnt_name[(i + 1) % 3 + 1]
    correct_n_neighbour = []
    for possible_type, j in correct_angle:
        if previous_n == 6:
            if possible_type[1 + (j + 1) % 3] == 3:
                if possible_type[1 + (j - 1) % 3] == [6, 3][m]:
                    correct_n_neighbour.append(possible_type)
        elif following_n == 6:
            if possible_type[1 + (j - 1) % 3] == 3:
                if possible_type[1 + (j + 1) % 3] == [3, 6][m]:
                    correct_n_neighbour.append(possible_type)
        else:
            if possible_type[1 + (j + 1) % 3] == [6, 3][m] and \
                    possible_type[1 + (j - 1) % 3] == [3, 6][m]:
                correct_n_neighbour.append(possible_type)

    if len(correct_n_neighbour) == 1:
        return correct_n_neighbour[0]

    raise Exception("RotatedDualGraphNodeType for neighbour not found.")


def neighbours_rdgnt_structure(grids: Dict[Tuple[int, ...],
                                           Dict[RDGNTName, List[RDGNTName]]]) \
                                            -> List[str]:
    text = ["from typing import Dict, Tuple, List\n\n",
            "ADJACENTS_RDGNT: Dict[Tuple[int, ...],\n",
            "                      ",
            "Dict[Tuple[int, ...], List[Tuple[int, ...]]]] = {\n"]
    for grid_type, rdgn_types in grids.items():
        text.append(f"    {grid_type}: {{\n")
        for rdgn_type, rdgnt_neighbours in rdgn_types.items():
            text.append(f"        {rdgn_type}: [\n")
            for i in range(len(rdgnt_neighbours)):
                text.append(f"            {rdgnt_neighbours[i]}")
                if i == len(rdgnt_neighbours) - 1:
                    text.append("],\n")
                else:
                    text.append(",\n")

        text.append("    },\n\n")

    text.append("}\n")

    return text


def generate_neighbours_rdgnt() -> List[str]:
    grids: Dict[Tuple[int, ...],
                Dict[RDGNTName, List[RDGNTName]]] = {}
    for grid_type in POSSIBLE_RDGNT.keys():
        polygon_types = build_polygontype_dic(grid_type)
        grids[grid_type] = build_precalculated_rdgnt_dic(
            POSSIBLE_RDGNT[grid_type], polygon_types)

    return neighbours_rdgnt_structure(grids)


def main() -> None:
    neighbours_rdgnt_text = generate_neighbours_rdgnt()
    now = datetime.now()
    formatted = now.strftime("%d-%m-%Y %H:%M:%S")
    constants_path = os.path.join(os.path.dirname(__file__),
                                  "constants_generated.py")

    with open(constants_path, "w") as file:
        file.write(f"# Generated by 'constants_script.py' [{formatted}]\n\n")
        file.writelines(neighbours_rdgnt_text)


if __name__ == "__main__":
    main()
