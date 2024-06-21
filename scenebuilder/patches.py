from numpy.typing import ArrayLike

import numpy as np
from matplotlib.patches import FancyArrow, Polygon
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt

from scenebuilder.entities import Drone, Obstacle


class Arrow:
    """Class to create a FancyArrow object"""

    def __init__(self, start: ArrayLike, end: ArrayLike, ax: plt.Axes) -> None:
        self.start = np.array(start)
        self.end = np.array(end)
        self.arrow: FancyArrow = None
        self.ax = ax

    def create_arrow(self) -> FancyArrow:
        ds = self.end - self.start
        self.arrow = self.ax.arrow(
            *self.start,
            ds[0],
            ds[1],
            length_includes_head=True,
            head_width=0.2,
            head_length=0.2,
            fc="k",
            ec="k",
            linestyle="-"
        )
        return self.arrow

    def update_arrow_position(self, new_start: tuple, new_end: tuple):
        new_x_start, new_y_start = new_start
        new_x_end, new_y_end = new_end

        dx = new_x_end - new_x_start
        dy = new_y_end - new_y_start

        self.arrow.set_data(x=new_x_start, y=new_y_start, dx=dx, dy=dy)

    def remove(self):
        self.arrow.remove()


class Marker:
    """Create an icon or marker patch to plot"""

    def __init__(self, position: ArrayLike, style: str, **kwargs) -> None:
        self.position = np.array(position)
        self.style = style
        self.marker: Line2D = None
        self.create_marker(**kwargs)
        self.original_marker = self.marker.get_marker()
        self.original_facecolor = self.marker.get_markerfacecolor()
        self.original_edgecolor = self.marker.get_markeredgecolor()
        self.original_color = self.marker.get_color()
        self.original_kwargs = kwargs.copy()  # Store the original kwargs

    def create_marker(self, **kwargs) -> Line2D:
        self.marker, = plt.plot(*self.position, self.style, **kwargs)
        return self.marker

    def update_position(self, new_position: tuple):
        self.position = new_position
        self.marker.set_xdata([self.position[0]])
        self.marker.set_ydata([self.position[1]])

    def remove(self):
        self.marker.remove()
    
    def set(self, **kwargs):
        self.marker.set(**kwargs)

    def reset_style(self):
        # Reset the marker style to the original
        self.marker.set_marker(self.original_marker)
        self.marker.set_color(self.original_color)
        self.marker.set_markerfacecolor(self.original_facecolor)
        self.marker.set_markeredgecolor(self.original_edgecolor)
        self.set(**self.original_kwargs)




class DronePatch:
    """Graphical representation of the Drone including start and end markers and an arrow connecting the two"""

    def __init__(self, drone: Drone, ax: plt.Axes) -> None:
        self.drone = drone
        self.marker_start: Marker = None
        self.marker_end: Marker = None

        self.arrow: Arrow = None
        self.ax = ax
        self._create_patches()

    def _create_patches(self) -> tuple:
        # plot the arrow
        self.marker_start = Marker(
            self.drone.position[:2], "g*"
        )  # Initial position in blue

        self.marker_end = Marker(self.drone.goal[:2], "b*")  # Goal position in red

        # Add an arrow with a line using the 'arrow' function
        self.arrow = Arrow(self.drone.position[:2], self.drone.goal[:2], self.ax)

        # self.patches = (self.marker_start, self.marker_end, self.arrow)
        # self.marker_start.create_marker()
        # self.marker_end.create_marker()
        self.arrow.create_arrow()
        # return (
        #     self.marker_start.create_marker(),
        #     self.marker_end.create_marker(),
        #     self.arrow.create_arrow(),
        # )

    def remove(self) -> None:
        """Remove the three patches"""
        self.marker_start.remove()
        self.marker_end.remove()
        self.arrow.remove()

    def patches(self):
        return self.marker_start.marker, self.marker_end.marker, self.arrow.arrow

    def update(self) -> None:
        self.marker_start.update_position(self.drone.position[:2])
        self.marker_end.update_position(self.drone.goal[:2])
        self.arrow.update_arrow_position(self.drone.position[:2], self.drone.goal[:2])


class ObstaclePatch:
    """
    Example usage:
    patch = ObstaclePatch(ax, building_instance, facecolor='blue', edgecolor='red', linewidth=2.0)
    """

    def __init__(self, ax:plt.Axes, building: Obstacle, **kwargs) -> None:
        self.ax = ax
        self.building = building
        self.polygon = Polygon(building.vertices, **kwargs)
        self.ax.add_patch(self.polygon)
        self.vertices = self.polygon.get_xy()[:-1]
        
        # Create markers for each vertex
        self.markers = self.create_markers()
        # Storing original colors
        self.original_facecolor = self.polygon.get_facecolor()
        self.original_edgecolor = self.polygon.get_edgecolor()

    def select(self):
        """Change appearance to represent selection."""
        self.polygon.set_facecolor((1, 0.4, 1, 0.7))
        self.polygon.set_edgecolor("black")

    def deselect(self):
        """Revert appearance to the original state."""
        self.polygon.set_facecolor(self.original_facecolor)
        self.polygon.set_edgecolor(self.original_edgecolor)

    def remove(self):
        self.polygon.remove()
        for marker in self.markers:
            marker.remove()

    def create_markers(self, **kwargs):
        markers = [Marker(vertex, 'bH', **kwargs) for vertex in self.vertices]
        return markers

    def update_visual(self):
        """Update the visual representation based on the building state."""
        self.vertices = self.building.vertices
        self.polygon.set_xy(self.vertices)
        if self.vertices.shape[0] != len(self.markers):
            for marker in self.markers:
                marker.remove()
            # self.markers = self.create_markers(markerfacecolor='None', markeredgecolor='b',markeredgewidth=3)
            self.markers = self.create_markers()

        else:
            for marker, vertex in zip(self.markers, self.building.vertices):
                marker.update_position(vertex)