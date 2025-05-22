# SemiGrid

A Python library for the representation of regular and semi-regular grids. The library provides grid generation, visualisation, and data assignment functionalities while supporting various types of tilings.



## Installation
You can clone this repository and use the library directly in your Python project.

```
git clone https://github.com/petrajiru/semigrid.git
cd semigrid
```

This library requires the following external Python packages:
- numpy
- shapely
- matplotlib


You can install these dependencies using pip:
```
pip install numpy shapely matplotlib
```

## Example Usage
This is a basic example demonstrating the creation of the grid, RGBA and numerical value assignment, and visualisation. Additional functionalities are illustrated in `example_script.py`.
```
from semigrid import SemiregularGrid
from semigrid import matplotlib_visualisation

grid = SemiregularGrid('3.3.3.4.4')
grid[(0, 0, 0)] = (1, 0, 0, 1)
grid[(0, 1, 0)] = 42

matplotlib_visualisation(grid)

```

## Project Structure
```
semigrid/
├── __init__.py
├── constants.py
├── dualgraphnode.py
├── gridpolygon.py
├── semiregulargrid_interface.py
├── semiregulargrid.py
└── visualisation.py
example_script.py
README.md
```

## Author
Petra Jírů - [petrajiru](https://github.com/petrajiru)