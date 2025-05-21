from semigrid import SemiregularGrid
from semigrid import matplotlib_visualisation
import math

from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt

grid_names = [
    '3.3.3.3.3.3',  # 6
    '4.4.4.4',      # 2
    '6.6.6',        # 3
    '3.3.3.3.6',    # 4
    '3.3.3.4.4',
    '3.3.4.3.4',    # 1
    '3.4.6.4',
    '3.6.3.6',
    '3.12.12',      # 5
    '4.6.12',
    '4.8.8']


# 1) Create a grid, color several cells and visualise them
# (press 'i' to see their indices)
grid1 = SemiregularGrid('3.3.4.3.4', edge_size=30)
for k in range(grid1.total_cell_types):
    grid1[(0, 0, k)] = (1, 0, 1, 1)  # pink origin

    for c in range(1, 4):
        grid1[(c, 0, k)] = (0, 1, 1, 1 - c * 0.3)  # teal i axis
        grid1[(0, c, k)] = (1, 1, 0, 1 - c * 0.3)  # yellow j axis

matplotlib_visualisation(grid1)


# 2) Create three different square grids and visualise them at once
square_grid = SemiregularGrid('4.4.4.4')
square_grid[(1, 0, 0)] = (1, 0, 0, 0.5)

square_grid_bigger = SemiregularGrid('4.4.4.4', edge_size=75)
square_grid_bigger[(1, 0, 0)] = (0, 1, 0, 0.5)

square_grid_45 = SemiregularGrid('4.4.4.4', grid_rotation=math.radians(45))

matplotlib_visualisation(square_grid, square_grid_45, square_grid_bigger,
                         figure_name="(2) Multiple square grids")


# 3) Create a grid, add numerical values to several cells + colour them, and
# finally, filter the cell numerical values to keep only the even ones
# (press 'n' to see the assigned numerical values)

hexagonal_grid = SemiregularGrid('6.6.6')
for i in range(5):
    for j in range(5):
        hexagonal_grid[(i, j, 0)] = i + j
        hexagonal_grid[(i, j, 0)] = (1, 1, 0, 1)

filtered_indices = hexagonal_grid.filter_num_values(lambda n: n % 2 == 0)
hexagonal_grid.delete_values(del_num=True, keep_indices=filtered_indices)

matplotlib_visualisation(hexagonal_grid,
                         figure_name="(3) Filtered numerical values")


# 4) Create a grid, color several cells and then filter them
grid4 = SemiregularGrid('3.3.3.3.6', edge_size=25)
for i in range(-2, 2):
    for j in range(-1, 2):
        for k in range(grid4.total_cell_types):
            grid4[(i, j, k)] = (1 - i % 2, j % 2, k / 10, 0.7)

matplotlib_visualisation(grid4, figure_name="(4.a) Colored cells")

filtered_indices = grid4.filter_rgba_values(lambda rgba: rgba[2] < 0.5)
grid4.delete_values(del_rgba=True, keep_indices=filtered_indices)
matplotlib_visualisation(grid4, figure_name="(4.b) Filtered colored cells")


# 5) Create a grid and color the adjacents of one particular cell
grid5 = SemiregularGrid('3.12.12', edge_size=20)
index = (1, 2, 0)
grid5[index] = (0, 1, 0, 1)

adjacents = grid5.adjacents(index)

for ijk in adjacents:
    grid5[ijk] = (0, 1, 0, 0.3)

matplotlib_visualisation(grid5, area_range=((-300, -100), (250, 300)),
                         figure_name="(5) Adjacents of a cell")


# 6) The usage of generating cell centres - create a triangular grid, generate
# coordinates of centres and use them as seeds to the voronoi graph
triangular_grid = SemiregularGrid(vertex_configuration='3.3.3.3.3.3')
centres_coords = triangular_grid.generate_centres(area_range=((0, 0),
                                                              (400, 300)))
voronoi_plot_2d(Voronoi(centres_coords))
plt.show()
