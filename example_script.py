from semigrid import SemiregularGrid
from semigrid import matplotlib_visualisation
import math


grids = [
    '3.3.3.3.3.3',
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


# 1) Create grids, color several cells and visualise them
for grid_name in grids:
    grid = SemiregularGrid(grid_name, 30, math.radians(45))
    for k in range(len(grid._rdgnt_names)):
        grid[(0, 0, k)] = (1, 0, 1, 1)  # pink origin
        
        for l in range(1, 4):
            grid[(l, 0, k)] = (0, 1, 1, 1 - l * 0.3)  # teal i axis
            grid[(0, l, k)] = (1, 1, 0, 1 - l * 0.3)  # yellow j axis

    grid[(5, 5, 1)] = (1, 0, 0, 1)

    matplotlib_visualisation(grid)



# 2) Create various square grids and visualise them at once
square_grid = SemiregularGrid('4.4.4.4')
square_grid[(1, 0, 0)] = (1, 0, 0, 0.5)

square_grid_bigger = SemiregularGrid('4.4.4.4', edge_size=75)
square_grid_bigger[(1, 0, 0)] = (0, 1, 0, 0.5)

square_grid_45 = SemiregularGrid('4.4.4.4', grid_rotation=math.radians(45))

matplotlib_visualisation(square_grid, square_grid_45, square_grid_bigger,
                         figure_name="Squares")



# 3} Create grid, add numeracial values to several cells + colour them, finally
# filter those cells so that only even values stay
hexagonal_grid = SemiregularGrid('6.6.6')
for i in range(5):
    for j in range(5):
        hexagonal_grid[(i, j, 0)] = i + j
        hexagonal_grid[(i, j, 0)] = (1, 1, 0, 1)  # original num values


filtered_indices = hexagonal_grid.filter_num_values(lambda number: number % 2 == 0)
hexagonal_grid.delete_values(del_num=True, keep_indices=filtered_indices)

matplotlib_visualisation(hexagonal_grid, figure_name="Filtered numerical values")


# ggg = SemiregularGrid('3.3.3.4.4', 100)

# ggg[(0, 0, 0)] = (0, 0, 1, 1)
# ggg[(0, 0, 1)] = (0.5, 0.5, 0.5, 0.5)  #
# ggg[(0, -1, 2)] = (0, 0, 1, 0.5)
# ggg[(-1, 0, 0)] = (0, 0, 1, 0.5)
# ggg[(1, 0, 0)] = (0, 0, 1, 0.5)

# ggg[(-3, -1, 2)] = (0, 1, 0, 1)
# ggg[(-3, 0, 0)] = (0, 1, 0, 0.5)
# ggg[(-3, -1, 1)] = (0.5, 0.5, 0.5, 0.5)  #
# ggg[(-2, -1,1)] = (0, 1, 0, 0.5)

# ggg[(3, 0, 1)] = (0, 1, 0.75, 1)
# ggg[(2, 0, 2)] = (0, 1, 0.75, 0.5)
# ggg[(3, 0, 0)] = (0, 1, 0.75, 0.5)
# ggg[(3, 0, 2)] = (0.5, 0.5, 0.5, 0.5)  #