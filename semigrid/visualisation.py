from semigrid.semiregulargrid import SemiregularGrid

import matplotlib.pyplot as plt
from matplotlib.backend_bases import Event, KeyEvent
from matplotlib.patches import Polygon
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from typing import Tuple, Any, Callable


class Visualisation:
    """
    Class for visualising the Semiregular grid interactively.
    It is based on matplotlib.
    """
    def __init__(self,
                 grids: Tuple[SemiregularGrid, ...],
                 area_range: Tuple[Tuple[float, float], Tuple[float, float]],
                 figure_name: str = "") -> None:
        self.grids = grids
        self.grid_names = self._get_grid_names()
        self.xlim_now = (area_range[0][0], area_range[1][0])
        self.ylim_now = (area_range[0][1], area_range[1][1])

        self.dragging = False

        self.show_index = False
        self.show_value = False
        self.show_center = False
        self.show_dual = False

        self.fig, self.ax = self._create_subplot(figure_name)
        self.colors = ['black', 'blue', 'green']

    def _get_grid_names(self) -> str:
        names_lst = [g.notation for g in self.grids]
        if len(names_lst) == 1:
            return names_lst[0]

        return ", ".join(names_lst)

    def _vis_edges(self, grid: SemiregularGrid) -> None:
        """For a given grid, visualise its edges. Add them to the plot."""
        edges = grid.generate_edges((
            (self.xlim_now[0], self.ylim_now[0]),
            (self.xlim_now[1], self.ylim_now[1])))
        g_i = self.grids.index(grid)
        line_collection = LineCollection(edges, colors=self.colors[g_i % len(
            self.colors)], linewidths=1)
        self.ax.add_collection(line_collection)

    def _vis_colored_polygons(self, grid: SemiregularGrid) -> None:
        """For a given grid, visualise polygons that have a color assigned.
        Add them to the plot."""
        for index, rgba_value in grid._rgba_values.items():
            dgn = grid.generated_cells.get(index)
            if dgn is not None:
                n = dgn.rdgnt_name[0]
                rotation = grid._rdgnt_dic[dgn.rdgnt_name].polygon_rotation
                polygon_vertices = grid._polygon_coords(dgn.coords, n,
                                                        rotation)
                self.ax.add_patch(Polygon(polygon_vertices,
                                          color=rgba_value[:3],
                                          alpha=rgba_value[-1]))

    def _vis_num_values(self, grid: SemiregularGrid) -> None:
        """For a given grid, visualise numerical values of the cells.
        Add them to the plot."""
        for index, num_value in grid._num_values.items():
            x, y = grid.index_to_coords(index)
            self.ax.text(x, y, str(num_value), fontsize=6,
                         clip_on=True, ha='center', fontweight='bold')

    def _vis_indices(self, grid: SemiregularGrid) -> None:
        """For a given grid, visualise indices of the cells.
        Add them to the plot."""
        grid_i = self.grids.index(grid)
        for ijk, dgn in grid.generated_cells.items():
            x, y = dgn.coords
            index = ijk if grid.notation not in ('4.4.4.4', '6.6.6') else \
                ijk[:-1]
            self.ax.text(x, y, str(index), fontsize=7, ha='center',
                         color=self.colors[grid_i % len(self.colors)],
                         clip_on=True)

    def _vis_centers(self, grid: SemiregularGrid) -> None:
        """For a given grid, visualise centers of the cells.
        Add them to the plot."""
        grid_i = self.grids.index(grid)
        for dgn in grid.generated_cells.values():
            x, y = dgn.coords
            self.ax.plot(x, y, marker='.', color=self.colors[grid_i % len(
                self.colors)])

    def _vis_dual(self, grid: SemiregularGrid) -> None:
        line_collection = LineCollection(grid._dual_graph, colors='red',
                                         linewidths=0.5)
        self.ax.add_collection(line_collection)

    def _for_each_grid(self, func: Callable[[SemiregularGrid], None]) -> None:
        for g in self.grids:
            func(g)

    def _visualise_grid(self) -> None:
        """
        Visualise grid - with numerical values/cell indices/centers (if meant
        to be shown) and with colored polygons (if they have color assigned).
        """
        self.ax.set_xlim(self.xlim_now)
        self.ax.set_ylim(self.ylim_now)
        self.ax.set_title(self.grid_names)

        for grid in self.grids:
            self._vis_edges(grid)
            self._vis_colored_polygons(grid)

            if self.show_dual:
                self._vis_dual(grid)
            if self.show_center:
                self._vis_centers(grid)
            if self.show_index:
                self._vis_indices(grid)
            if self.show_value:
                self._vis_num_values(grid)

    def _on_press(self, event: Event) -> Any:
        self.dragging = True

    def _on_release(self, event: Event) -> Any:
        self.dragging = False

    def _on_motion(self, event: Event) -> Any:
        if self.dragging:
            self.ax.clear()
            self._visualise_grid()
            plt.draw()

    def _on_draw(self, event: Event) -> Any:
        self.xlim_now = self.ax.get_xlim()
        self.ylim_now = self.ax.get_ylim()

    def _on_key(self, event: Event) -> Any:
        if isinstance(event, KeyEvent):
            if event.key == 't':
                self.show_center = not self.show_center
            elif event.key == 'i':
                self.show_index = not self.show_index
            elif event.key == 'n':
                self.show_value = not self.show_value
            elif event.key == 'd':
                self.show_dual = not self.show_dual

            if event.key in ('t', 'i', 'n', 'r', 'd'):
                if event.key == 't' and self.show_center:
                    self._for_each_grid(self._vis_centers)
                elif event.key == 'i' and self.show_index:
                    self._for_each_grid(self._vis_indices)
                elif event.key == 'n' and self.show_value:
                    self._for_each_grid(self._vis_num_values)
                elif event.key == 'd' and self.show_dual:
                    self._for_each_grid(self._vis_dual)
                else:
                    self.ax.clear()
                    self._visualise_grid()

                plt.draw()

    def _create_subplot(self, figure_name: str) -> Tuple[Figure, Axes]:
        """Create fig and ax and set them."""
        fig, ax = plt.subplots()

        fig.text(0.33, 0.02, 'Show/hide: [i] [n] [t] [d]', ha='center',
                 fontsize=8)
        fig.text(0.66, 0.02, 'Reload: [r]', ha='center', fontsize=8)

        assert fig.canvas.manager is not None
        fig.canvas.manager.set_window_title(figure_name)

        fig.canvas.mpl_connect('draw_event', self._on_draw)
        fig.canvas.mpl_connect('key_press_event', self._on_key)
        fig.canvas.mpl_connect('button_press_event', self._on_press)
        fig.canvas.mpl_connect('button_release_event', self._on_release)
        fig.canvas.mpl_connect('motion_notify_event', self._on_motion)

        return fig, ax

    def visualise(self) -> None:
        """
        Pop up a figure that visualises the grid.
        """
        self._visualise_grid()
        plt.show()


def _increase_window(window_range: Tuple[Tuple[float, float],
                                         Tuple[float, float]]) \
                                            -> Tuple[Tuple[float, float],
                                                     Tuple[float, float]]:
    """Increase the window so it is in the ratio 3:4."""
    min_x, min_y = window_range[0]
    max_x, max_y = window_range[1]
    x_length = max_x - min_x
    y_length = max_y - min_y
    ideal_x_length = (y_length / 3)*4
    ideal_y_length = (x_length/4)*3

    new_max = (min_x + ideal_x_length, max_y) \
        if x_length < ideal_x_length else (max_x, min_y + ideal_y_length)

    return (window_range[0], new_max)


def matplotlib_visualisation(*grids: SemiregularGrid,
                             area_range: Tuple[Tuple[float, float],
                                               Tuple[float, float]]
                             = ((-100, -75), (100, 75)),
                             figure_name: str = "") -> None:
    """Visualise the grid interactively using matplotlib.
    Zoom in/out and move along the grid. Press keys for another functionality:
        * 'i' to show/hide the cell's indices
        * 'n' to show/hide the cell's numerical values
        * 't' to show/hide the marked centers of the cells
        * 'r' to reload the grid
    """
    min_xy, max_xy = area_range
    if min_xy[0] >= max_xy[0] or min_xy[1] >= max_xy[1]:
        print("Invalid area range: ", area_range)
        return

    window = _increase_window(area_range)

    v = Visualisation(grids=grids, area_range=window, figure_name=figure_name)
    v.visualise()
