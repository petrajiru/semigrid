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
- shapely.geometry
- matplotlib
    - matplotlib.pyplot
    - matplotlib.backend_bases
    - matplotlib.patches
    - matplotlib.collections
    - matplotlib.figure
    - matplotlib.axes

You can install these dependencies using pip:
```
pip install numpy shapely matplotlib
```

## Example Usage
This is the very basic example usage showing the creation of the grid, rgba and value assignment, and visualisation. Other functionalities are shown in `example_script.py`.
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
├── constants_generated.py
├── constants_script.py
├── constants.py
├── dualgraphnode.py
├── gridpolygon.py
├── semiregulargrid_interface.py
├── semiregulargrid.py
└── visualisation.py
README.md
example_script.py
```

## Author
Petra Jírů - [petrajiru](https://github.com/petrajiru)