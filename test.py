from semigrid import SemiregularGrid
from semigrid import matplotlib_visualisation
import math
import random

grids = ['3.3.3.3.3.3',
         '4.4.4.4',
         '6.6.6',
         '3.3.3.3.6', 
         '3.3.3.4.4', 
         '3.3.4.3.4', 
         '3.4.6.4', 
         '3.6.3.6', 
         '3.12.12', 
         '4.6.12', 
         '4.8.8']

for _ in range(20):
    for g_notion in grids:
        rotation = random.randint(-200, round(math.pi * 7))
        edge = random.randint(0, 1000)
        g = SemiregularGrid(g_notion, grid_rotation = rotation, edge_size = edge)

        print("         name     *   rad -> degrees -> degrees [0, 360] * edge")
        print(f"GRID * {g_notion} * {rotation} -> {math.degrees(rotation)} -> [{math.degrees(rotation)%360}] * {edge}")
        
        min_x = random.randint(-2000, 5000)
        min_y = random.randint(-2000, 5000)
        max_x = random.randint(-200, 5000)
        max_y = random.randint(-400, 5000)
        e = g.generate_edges(((min_x, min_y), (max_x, max_y)))
        p = g.generate_polygons(((min_x, min_y), (max_x, max_y)))
        
        print(f"[({min_x}, {min_y}), ({max_x}, {max_y})] edges: {len(e)}")
        print(f"[({min_x}, {min_y}), ({max_x}, {max_y})] ngons: {len(p)}")
        print('..............................................')
