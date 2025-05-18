"""
(vertex configuration): [
    (n-gon, adjacent n-gon1, adjacent n-gon2,... rotation of DualGridNodeType),
    (n-gon, adjacent n-gon1, adjacent n-gon2,... rotation of DualGridNodeType),
    ...
    ]

* rotation = 0 means that the polar coordinate of the first neighbour's
    centre is (r, 0)
* rotation is in degrees
"""
from typing import Dict, Tuple, List
import math

# a height of...
TRIANGLE_H = math.sqrt(3)/2  # ...equilateral TRIANGLE
TRIANGLE_H_8 = 1/(2*math.tan(math.radians(22.5)))  # ...triangle in OCTAGON
TRIANGLE_H_12 = 1/(2*math.tan(math.radians(15)))  # ...triangle in DODECAHEDRON

COS_RAD_30 = math.cos(math.radians(30))
COS_RAD_60 = math.cos(math.radians(60))
SIN_RAD_30 = math.sin(math.radians(30))
SIN_RAD_60 = math.sin(math.radians(60))


# indexing
UNIT_VECTORS: Dict[Tuple[int, ...],
                   Tuple[Tuple[float, float], Tuple[float, float]]] = {
    (3, 3, 3, 3, 3, 3): ((1, 0), (0.5, TRIANGLE_H)),
    (4, 4, 4, 4): ((1, 0), (0, 1)),
    (6, 6, 6): ((2*TRIANGLE_H, 0), (TRIANGLE_H, 3/2)),

    (3, 3, 3, 3, 6): ((2.5, -TRIANGLE_H), (2, 2*TRIANGLE_H)),
    (3, 3, 3, 4, 4): ((1, 0), (0.5, 1 + TRIANGLE_H)),
    (3, 3, 4, 3, 4): (
        (0.5 + TRIANGLE_H, - 0.5 - TRIANGLE_H),
        (0.5 + TRIANGLE_H, 0.5 + TRIANGLE_H)),
    (3, 4, 6, 4): (
        (2*TRIANGLE_H + 1, 0),
        (TRIANGLE_H + 0.5, 1.5 + TRIANGLE_H)),
    (3, 6, 3, 6): ((2, 0), (1, 2 * TRIANGLE_H)),
    (3, 12, 12): (
        (2*TRIANGLE_H_12, 0),
        (TRIANGLE_H_12,
         TRIANGLE_H + TRIANGLE_H_12 + 0.5)),

    (4, 6, 12): (
        (TRIANGLE_H_12 + 2 * TRIANGLE_H + 0.5,
         - 0.5 - TRIANGLE_H_12),
        (TRIANGLE_H_12 + 2 * TRIANGLE_H + 0.5,
         0.5 + TRIANGLE_H_12)),

    (4, 8, 8): (
        (TRIANGLE_H_8 + 0.5, - TRIANGLE_H_8 - 0.5),
        (TRIANGLE_H_8 + 0.5, TRIANGLE_H_8 + 0.5))
}

UNIT_BLOCK_CELLS_OFFSET: Dict[Tuple[int, ...],
                              Dict[Tuple[int, ...], Tuple[float, float]]] = {
    (4, 4, 4, 4): {
        (4, 4, 4, 4, 4, 0): (0, 0)},
    (6, 6, 6): {
        (6, 6, 6, 6, 6, 6, 6, 0): (0, 0)},
    (3, 3, 3, 3, 3, 3): {
        (3, 3, 3, 3, 30): (0, 0),
        (3, 3, 3, 3, 90): (0.5, TRIANGLE_H/3)},

    (3, 3, 3, 3, 6): {
        (6, 3, 3, 3, 3, 3, 3, 30): (0, 0),
        (3, 3, 3, 6, 30): (0, 4/3 * TRIANGLE_H),
        (3, 3, 3, 6, 90): (1.5, -1/3 * TRIANGLE_H),
        (3, 3, 3, 6, 150): (1, 4/3 * TRIANGLE_H),
        (3, 3, 3, 6, 210): (-0.5, 5/3 * TRIANGLE_H),
        (3, 3, 3, 6, 270): (1, -2/3 * TRIANGLE_H),
        (3, 3, 3, 6, 330): (1, 2/3 * TRIANGLE_H),
        (3, 3, 3, 3, 30): (1.5, 1/3 * TRIANGLE_H),
        (3, 3, 3, 3, 90): (0.5, 5/3 * TRIANGLE_H)},

    (3, 3, 3, 4, 4): {
        (4, 3, 4, 3, 4, 90): (0, 0),
        (3, 3, 3, 4, 30): (0, 0.5 + TRIANGLE_H/3),
        (3, 3, 3, 4, 210): (0.5, 0.5 + 2/3 * TRIANGLE_H)},

    (3, 3, 4, 3, 4): {
        (4, 3, 3, 3, 3, 30): (
            (TRIANGLE_H/3 + 0.5) * COS_RAD_30,
            (TRIANGLE_H/3 + 0.5) * SIN_RAD_30),
        (4, 3, 3, 3, 3, 60): (
            -(TRIANGLE_H/3 + 0.5) * COS_RAD_30,
            (TRIANGLE_H/3 + 0.5) * SIN_RAD_30),
        (3, 3, 4, 4, 0): (- TRIANGLE_H/3, 2/3 * TRIANGLE_H + 0.5),
        (3, 3, 4, 4, 90): (0, -2/3 * TRIANGLE_H),
        (3, 3, 4, 4, 180): (TRIANGLE_H/3, 2/3 * TRIANGLE_H + 0.5),
        (3, 3, 4, 4, 270): (0, 0)},

    (3, 12, 12): {
        (12, 3, 12, 3, 12, 3, 12, 3, 12, 3, 12, 3, 12, 30): (0, 0),
        (3, 12, 12, 12, 30): (0, TRIANGLE_H_12 + TRIANGLE_H/3),
        (3, 12, 12, 12, 90): (TRIANGLE_H_12, 0.5 + 2/3 * TRIANGLE_H)},

    (3, 4, 6, 4): {
        (6, 4, 4, 4, 4, 4, 4, 0): (0, 0),
        (4, 3, 6, 3, 6, 30): (
            -(TRIANGLE_H + 0.5) * COS_RAD_60, (TRIANGLE_H + 0.5) * SIN_RAD_60),
        (4, 3, 6, 3, 6, 90): (TRIANGLE_H + 0.5, 0),
        (4, 3, 6, 3, 6, 150): (
            (TRIANGLE_H + 0.5) * COS_RAD_60, (TRIANGLE_H + 0.5) * SIN_RAD_60),
        (3, 4, 4, 4, 30): (TRIANGLE_H + 0.5, 0.5 + TRIANGLE_H/3),
        (3, 4, 4, 4, 90): (0, 1 + 2/3 * TRIANGLE_H)},

    (3, 6, 3, 6): {
        (6, 3, 3, 3, 3, 3, 3, 30): (0, 0),
        (3, 6, 6, 6, 30): (0, 4/3 * TRIANGLE_H),
        (3, 6, 6, 6, 90): (1, 2/3 * TRIANGLE_H)},

    (4, 6, 12): {
        (12, 4, 6, 4, 6, 4, 6, 4, 6, 4, 6, 4, 6, 30): (0, 0),
        (6, 4, 12, 4, 12, 4, 12, 0): (
            - COS_RAD_60 * (TRIANGLE_H + TRIANGLE_H_12),
            SIN_RAD_60 * (TRIANGLE_H + TRIANGLE_H_12)),
        (6, 4, 12, 4, 12, 4, 12, 60): (
            COS_RAD_60 * (TRIANGLE_H + TRIANGLE_H_12),
            SIN_RAD_60 * (TRIANGLE_H + TRIANGLE_H_12)),
        (4, 6, 12, 6, 12, 0): (0, 0.5 + TRIANGLE_H_12),
        (4, 6, 12, 6, 12, 60): (
            - COS_RAD_30 * (0.5 + TRIANGLE_H_12),
            SIN_RAD_30 * (0.5 + TRIANGLE_H_12)),
        (4, 6, 12, 6, 12, 120): (
            COS_RAD_30 * (0.5 + TRIANGLE_H_12),
            SIN_RAD_30 * (0.5 + TRIANGLE_H_12))},

    (4, 8, 8): {
        (8, 4, 8, 4, 8, 4, 8, 4, 8, 0): (0, 0),
        (4, 8, 8, 8, 8, 0): (0, 0.5 + TRIANGLE_H_8)},
}


POSSIBLE_RDGNT: Dict[Tuple[int, ...], List[Tuple[int, ...]]] = {
    (4, 4, 4, 4): [(4, 4, 4, 4, 4, 0)],
    (6, 6, 6): [(6, 6, 6, 6, 6, 6, 6, 0)],
    (3, 3, 3, 3, 3, 3): [
        (3, 3, 3, 3, 30),
        (3, 3, 3, 3, 90)],

    (3, 3, 3, 3, 6): [
        (6, 3, 3, 3, 3, 3, 3, 30),
        (3, 3, 3, 6, 210),
        (3, 3, 3, 6, 30),
        (3, 3, 3, 3, 90),
        (3, 3, 3, 6, 150),
        (3, 3, 3, 6, 330),
        (3, 3, 3, 3, 30),
        (3, 3, 3, 6, 90),
        (3, 3, 3, 6, 270)],

    (3, 3, 3, 4, 4): [
        (4, 3, 4, 3, 4, 90),
        (3, 3, 3, 4, 30),
        (3, 3, 3, 4, 210)],

    (3, 3, 4, 3, 4): [
        (3, 3, 4, 4, 270),
        (4, 3, 3, 3, 3, 60),
        (3, 3, 4, 4, 0),
        (3, 3, 4, 4, 180),
        (4, 3, 3, 3, 3, 30),
        (3, 3, 4, 4, 90)],

    (3, 12, 12): [
        (12, 3, 12, 3, 12, 3, 12, 3, 12, 3, 12, 3, 12, 30),
        (3, 12, 12, 12, 30),
        (3, 12, 12, 12, 90)],

    (3, 4, 6, 4): [
        (6, 4, 4, 4, 4, 4, 4, 0),
        (4, 3, 6, 3, 6, 30),
        (3, 4, 4, 4, 90),
        (4, 3, 6, 3, 6, 150),
        (3, 4, 4, 4, 30),
        (4, 3, 6, 3, 6, 90)],

    (3, 6, 3, 6): [
        (6, 3, 3, 3, 3, 3, 3, 30),
        (3, 6, 6, 6, 30),
        (3, 6, 6, 6, 90)],

    (4, 6, 12): [
        (12, 4, 6, 4, 6, 4, 6, 4, 6, 4, 6, 4, 6, 30),
        (4, 6, 12, 6, 12, 60),
        (6, 4, 12, 4, 12, 4, 12, 0),
        (4, 6, 12, 6, 12, 0),
        (6, 4, 12, 4, 12, 4, 12, 60),
        (4, 6, 12, 6, 12, 120)],

    (4, 8, 8): [
        (8, 4, 8, 4, 8, 4, 8, 4, 8, 0),
        (4, 8, 8, 8, 8, 0)],
}
