import matplotlib.pyplot as plt

from matplotlib.lines import Line2D
from typing import List
import numpy as np
from scenebuilder.entities import Obstacle, Drone
from scenebuilder.patches import ObstaclePatch, DronePatch, Marker


class PatchManager:
    def __init__(self, ax: plt.Axes):
        self.ax = ax
        self.building_patches: dict[Obstacle, ObstaclePatch] = {}
        self.drone_patches: dict[Drone, DronePatch] = {}
        # self.temp_drone_starts:list[Line2D] = []
        self.current_building_vertices: list[Marker] = []
        self.drone_start = None

    def add_building_patch(self, building: Obstacle, **kwargs) -> None:
        building_patch = ObstaclePatch(
            self.ax,
            building,
            edgecolor=kwargs.get("edgecolor", (0, 0, 0, 1)),
            facecolor=kwargs.get("facecolor", (0, 0, 1, 0.5)),
            closed=kwargs.get("closed", True),
            linewidth=kwargs.get("linewidth", 2.0),
            picker=kwargs.get("picker", True),
        )
        # self.ax.add_patch(patch)
        self.building_patches[building] = building_patch

    def add_building_vertex(self, vertex: tuple) -> None:
        point = Marker(vertex, "go")
        self.current_building_vertices.append(point)

    def get_building_patch(self, building: Obstacle) -> ObstaclePatch:
        """Obtains the paftch for the building passed as argument
        and returns it. If the patch doesn't exist, returns KeyError.
        """
        return self.building_patches[building]

    def get_building_from_patch(self, patch: plt.Polygon) -> Obstacle:
        """Obtains the building from the patch passed as argument"""
        for building, building_patch in self.building_patches.items():
            if building_patch.polygon == patch:
                # call the selected building setter to highlight the building
                return building

    def make_building(self) -> Obstacle:
        """Create a building from the current vertices"""
        if not len(self.current_building_vertices) >= 3:
            return
        vertices = np.array(
            [point.position for point in self.current_building_vertices]
        )
        building = Obstacle(vertices)
        self.add_building_patch(building)
        self.clear_building_vertices()
        return building

    def make_drone(self) -> Drone:
        return Drone(ID=f"V{len(self.drones)}", position=None, goal=None)

    def add_drone_patch(self, drone: Drone, **kwargs) -> None:
        # Similar logic for adding drone patches
        drone_patch = DronePatch(drone, self.ax)
        # patches = drone_patch.create_patches()
        self.drone_patches[drone] = drone_patch

    def add_temp_drone_start(self, point: list) -> None:
        # self.temp_drone_starts.append(point)
        self.drone_start = Marker(point, style="ko")

    def remove_temp_drone_start(self) -> None:
        if self.drone_start:
            self.drone_start.remove()
            self.drone_start = None

    def _remove_markers_from_list(self, lst: List[Line2D]) -> None:
        for element in lst:
            element.remove()
        lst.clear()

    def redraw_drone(self, drone: Drone) -> None:
        self.drone_patches[drone].update()

    def redraw_building(self, building: Obstacle) -> None:
        self.building_patches[building].update_visual()

    def remove_building_patch(self, building: Obstacle):
        if building in self.building_patches:
            self.building_patches[building].remove()
            del self.building_patches[building]

    def remove_drone_patch(self, drone: Drone) -> None:
        """Remove drone patch from the figure and the patches dictionary
        and remove the patches from the figure
        """
        self.drone_patches.pop(drone).remove()

    def clear_building_vertices(self):
        self._remove_markers_from_list(self.current_building_vertices)

    def clear_all(self):
        for patch in self.building_patches.values():
            patch.remove()
        for patch in self.drone_patches.values():
            patch.remove()
        self.remove_temp_drone_start()
        self.building_patches.clear()
        self.drone_patches.clear()
