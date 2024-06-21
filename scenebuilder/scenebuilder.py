from __future__ import annotations

import matplotlib.pyplot as plt

import numpy as np

from scenebuilder.entities import Drone, Obstacle
from scenebuilder.utils import (
    distance_between_points,
    create_json,
    get_case_from_dict,
    convert_from_geojson,
)
from scenebuilder.utils import load_from_json, validate_json_path
from scenebuilder.patch_manager import PatchManager
from scenebuilder.actions_stack import ActionsStack
from scenebuilder.ui_components import UIComponents
from scenebuilder.observer_utils import Observer, Observable
from threading import Timer
from pathlib import Path
import traceback
import os


class SceneBuilder(Observer, Observable):

    CLICK_THRESHOLD = 0.14
    FIG_SIZE = (8, 8.5)
    AXIS_LIMITS = (-5, 5)
    PIXEL_TOLERANCE = 20 #within this many pixels a click is considered "on" a line or point
    HEIGHT = 1.2 # obstacle height
    def __init__(self):
        # initialise Observable (Observer has no init)
        super().__init__()
        self._selected_building: Obstacle = None
        self.original_colors: dict = {}
        # Setup the default plot
        self._plot_setup()
        # Define variables
        self._setup_data()

        # Connect event handlers
        self._connect_event_handlers()

    def load_scene(self, path: str) -> None:
        """Populates the scene with the obstacles and drones in the specified json
        path: path to compatible json file"""
        self._reset()
        if path.endswith(".geojson"):
            case_info = convert_from_geojson(path)
        else:
            case_info = load_from_json(path)
        drones, buildings = get_case_from_dict(case_info)
        self.drones = drones
        self.buildings = buildings
        for building in self.buildings:
            self.patch_manager.add_building_patch(building)
        for drone in self.drones:
            self.patch_manager.add_drone_patch(drone)
        self._update()

    def draw_scene(self):
        """Draw the scene."""
        plt.show()

    def set_lims(self, new_lims:tuple):
        self.ax.set_xlim(new_lims)
        self.ax.set_ylim(new_lims)

    def _plot_setup(self):
        fig = plt.figure(figsize=self.FIG_SIZE)
        ax = fig.add_subplot(111)

        fig.subplots_adjust(bottom=0.1, top=0.85)

        ax.set_xlim(self.AXIS_LIMITS)
        ax.set_ylim(self.AXIS_LIMITS)
        ax.set_box_aspect(1)
        ax.grid(color="k", linestyle="-", linewidth=0.5, which="major")
        ax.grid(color="k", linestyle=":", linewidth=0.5, which="minor")
        # ax.grid(True)
        ax.minorticks_on()

        # Add instructions
        instructions = (
            "Instructions:\n"
            "'b': switch to building mode, click to place vertices of building\n"
            "Tab: complete a building, \n"
            "'d': switch to drone mode. "
            "'esc': clear unwanted points."
        )

        fig.text(
            0.2,
            0.91,
            instructions,
            fontsize=10,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )
        # modifiable/interactive ui elements are in ui_components.py

        self.fig, self.ax = fig, ax

        return None

    def _setup_data(self) -> None:
        """define additional attributes"""
        self.ui_components = UIComponents(self.ax)
        self.ui_components.add_observer(self)

        # this line makes sure the current axes are the main ones
        plt.sca(self.ax)

        self.patch_manager = PatchManager(self.ax)
        self.output_path = "scenebuilder.json"

        self.timer: Timer | None = None

        self.drones: list[Drone] = []
        self.buildings: list[Obstacle] = []
        self.current_drone = None
        self.mode = "building"  # 'building', 'drone', or None
        self.actions_stack = ActionsStack()  # New line to track the actions

        self.selected_drone: Drone | None = None
        self.initial_click_position = None
        self.selected_vertex = None
        self.warning = self.ax.annotate(
            "WARNING, No Drones!",
            xy=(0.5, 0.5),
            xycoords="axes fraction",
            fontsize=12,
            fontweight="bold",
            color="red",
            ha="center",
            bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=1),
            wrap=True,
        )

        self.warning.set_visible(False)  # Start with warning hidden

        return None

    def _set_output_path(self, path: str, exit=False, skip_check=False) -> None:
        """Set output path to validated path. call sys.exit() if exit is True and path is invalid"""
        try:
            if not skip_check:
                # Validate the path if not skipping
                response = validate_json_path(path, exit)
                result = response["result"]
                # if path invalid, don't set
                if result == 0:
                    return
        finally:
            # This block runs whether validation was skipped, passed, or failed.
            self.output_path = path
            self._show_warning(f"Set new output path\n{path}", 3, color="g")

    @property
    def selected_building(self):
        return self._selected_building

    @selected_building.setter
    def selected_building(self, new_building: Obstacle):
        """Highlight selected building in pink or deselect it if it is already selected.
        This function is called when a building is selected or deselected.
        patch: ObstaclePatch
        Return: None
        """
        if self._selected_building:
            current_patch = self.patch_manager.get_building_patch(
                self._selected_building
            )
            current_patch.deselect()
        if new_building:
            new_building_patch = self.patch_manager.get_building_patch(new_building)
            new_building_patch.select()
        self._selected_building = new_building
        self._update()

    def _hide_warning(self):
        self.warning.set_visible(False)
        self._update()

    def _connect_event_handlers(self) -> None:
        # supported values are 'resize_event', 'draw_event', 'key_press_event', 'key_release_event', 'button_press_event', 'button_release_event', 'scroll_event', 'motion_notify_event', 'pick_event', 'figure_enter_event', 'figure_leave_event', 'axes_enter_event', 'axes_leave_event', 'close_event'
        self.on_pick = self.fig.canvas.mpl_connect("pick_event", self._on_pick)
        self.on_click = self.fig.canvas.mpl_connect(
            "button_press_event", self._on_click
        )
        self.on_key = self.fig.canvas.mpl_connect("key_press_event", self._on_key_press)
        self.fig.canvas.mpl_connect("button_release_event", self._on_button_release)
        self.fig.canvas.mpl_connect("motion_notify_event", self._on_mouse_move)
        # self.resize=self.fig.canvas.mpl_connect('resize_event', lambda x:print("tool triggered"))
        self.ax.callbacks.connect("xlim_changed", self._on_axes_change)
        self.ax.callbacks.connect("ylim_changed", self._on_axes_change)
        return None
    
    def _on_axes_change(self, event):
        self._reset_click_threshold()
        # print('axes changed')

    def _disconnect_event_handlers(self) -> None:
        self.fig.canvas.mpl_disconnect(self.on_click)
        self.fig.canvas.mpl_disconnect(self.on_key)
        self.fig.canvas.mpl_disconnect(self.on_pick)

        return None

    def _handle_vertex_movement(self, event):
        """Returns True if a click is near a vertex of an obstacle"""
        if not self.buildings:
            return False

        # Find the closest vertex
        closest_building, closest_vertex_index = self._get_closest_vertex(
            [event.xdata, event.ydata]
        )

        # Check if the closest vertex is close enough to be selected
        dist = distance_between_points(
            closest_building.vertices[closest_vertex_index][:2],
            [event.xdata, event.ydata],
        )
        if dist >= self.CLICK_THRESHOLD:
            return False

        self.selected_vertex = closest_vertex_index
        self.initial_click_position = None
        self.selected_building = closest_building
        return True

    def _get_closest_vertex(self, point):
        """Find the closest vertex to the given point."""
        all_vertices = (
            (building, j)
            for building in self.buildings
            for j in range(len(building.vertices))
        )

        return min(
            all_vertices,
            key=lambda x: distance_between_points(x[0].vertices[x[1]][:2], point),
        )

    def _handle_drone_movement(self, event) -> bool:
        # Check if a drone starting or ending point was clicked
        point = [event.xdata, event.ydata]
        for drone in self.drones:
            start_dist = distance_between_points(drone.position[:2], point)
            end_dist = distance_between_points(drone.goal[:2], point)
            if (
                start_dist < self.CLICK_THRESHOLD
            ):  # This threshold determines how close the click should be to consider a match
                self.selected_drone = drone
                self.dragging_drone_point = "start"
                return True
            elif end_dist < self.CLICK_THRESHOLD:
                self.selected_drone = drone
                self.dragging_drone_point = "end"
                return True

            # Check if the click is on the arrow connecting the drone start and end points
            if drone.click_near_arrow(
                drone.position[:2],
                drone.goal[:2],
                event,
                threshold=self.CLICK_THRESHOLD,
            ):
                self.selected_drone = drone
                self.dragging_drone_point = "arrow"
                self.initial_click_position = point
                return True

        self.selected_drone = None
        self.dragging_drone_point = None
        return False

    def _handle_building_placement(self, event) -> None:
        self.selected_building = None
        if self.current_drone:
            self.patch_manager.remove_temp_drone_start()
            self.current_drone = None
        # Add a corner to the current building at the click location
        # plot the point in the patch manager
        self.patch_manager.add_building_vertex((event.xdata, event.ydata))
        self._update()
        return None

    def _handle_drone_placement(self, event) -> None:
        # clear any buildings before starting drones
        # Add a drone at the click location
        self.selected_building = None
        if self.current_drone is None:
            # initialise the drone
            # what to do when we draw the initial position of the drone
            # This is the initial position of the drone
            # clear all other temporary elements
            self.patch_manager.clear_building_vertices()
            self.current_drone = Drone(
                ID=f"V{len(self.drones)}", position=None, goal=None
            )
            self.current_drone.position = np.array([event.xdata, event.ydata, 0.5])
            self.patch_manager.add_temp_drone_start(self.current_drone.position[:2])
            self._update()
        else:
            # drone initial position is already defined, now add the destination (goal)
            # This is the goal position of the drone
            self.current_drone.goal = np.array([event.xdata, event.ydata, 0.5])

            self.drones.append(self.current_drone)
            self.actions_stack.add_action("drone", self.current_drone)
            self.patch_manager.remove_temp_drone_start()

            # add drone patch to patch_manager
            self.patch_manager.add_drone_patch(self.current_drone)
            self.current_drone = None
            self._update()
        return None

    
    def _reset_click_threshold(self)->None:
            """Convert pixel tolerance to data coordinates and call Obstacle's insert_vertex"""
            # Get the axis limits
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()

            # Calculate the display-to-data ratio for both x and y axes
            bbox = self.ax.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
            width_pixels = bbox.width * self.fig.dpi
            height_pixels = bbox.height * self.fig.dpi

            x_ratio = (xlim[1] - xlim[0]) / width_pixels
            y_ratio = (ylim[1] - ylim[0]) / height_pixels

            # Use the larger of the two ratios to ensure tolerance covers both dimensions
            threshold = self.PIXEL_TOLERANCE * max(x_ratio, y_ratio)
            self.CLICK_THRESHOLD = threshold
            return None

    
    def _add_new_vertex(self, event):
        """Tries to add a new vertex if user clicks near an building edge"""
        position = (event.xdata, event.ydata)
        for building in self.buildings:
            index = building.find_insert_index(position, self.CLICK_THRESHOLD)
            if index:
                building.insert_vertex(position, index)
                # Redraw the building if a vertex was added
                self.patch_manager.redraw_building(building)
                self._update()
                return True

    def _handle_deselect(self, event):
        if self.selected_building:
            if not self.selected_building.contains_point([event.xdata, event.ydata]):
                self.selected_building = None
            return True

    def _on_click(self, event):
        """
        This method is called when a click is detected on the plot.
        The event object contains information about the click, such as its position.
        You can use this information to add new elements to the plot, such as a new building or a new drone.
        #NOTE ORDER MATTERS, events will be handled in the order they are listed in this method"""
        # If clicked outside of the plot, do nothing
        # if not event.xdata or not event.ydata:
        #     return
        if event.inaxes != self.ax:
            return

        # handle moving building vertices
        if self._handle_vertex_movement(event):
            return

        # add a new vertex if near a building edge and allow moving it around with the mouse...
        # by calling the vertex movement handler again
        if self._add_new_vertex(event):
            self._handle_vertex_movement(event)
            return

        # if a building is selected and we click outside of it, it is deselected (but nothing else happens)
        if self._handle_deselect(event):
            return

        # Check if a drone was clicked and handle its movement if necessary
        if self._handle_drone_movement(event):
            return
        # Check if a building was clicked and handle its movement if necessary

        # Proceed with building placement
        if self.mode == "building":
            self._handle_building_placement(event)
            return

        # Proceed with drone placement
        elif self.mode == "drone":
            self._handle_drone_placement(event)
            return

        # Update the plot
        self._update()

    def _on_pick(self, event):
        # Check if the picked artist is a Polygon (optional but can be useful)
        if not isinstance(event.artist, plt.Polygon):
            return

        # polygon = event.artist
        building = self.patch_manager.get_building_from_patch(event.artist)
        self.selected_building = building

        self.initial_click_position = [event.mouseevent.xdata, event.mouseevent.ydata]

    def _on_mouse_move(self, event):
        # check to make sure the mouse is still in the main axes
        # and not over a button or other axes object
        # or outside the axes altogether
        if event.inaxes != self.ax:
            return

        point = [event.xdata, event.ydata]

        ##########################################################################################
        # move the vertex if one is selected
        if self.selected_building is not None and self.selected_vertex is not None:
            # # move the relevent vertex
            self.selected_building.move_vertex(self.selected_vertex, point)
            self.patch_manager.redraw_building(self.selected_building)

            self._update()  # Redraw to show the moved vertex

        ###########################################################################################
        # Move the drone
        elif self.selected_drone:
            if self.dragging_drone_point == "start":
                self.selected_drone.position = np.array([*point, 0.5])

            elif self.dragging_drone_point == "end":
                self.selected_drone.goal = np.array([*point, 0.5])
            elif self.dragging_drone_point == "arrow":
                # Move both start and end points, and update all corresponding patches
                ds = np.array(point) - np.array(self.initial_click_position)

                self.selected_drone.move_whole_drone(ds)

            self.initial_click_position = point
            # This will redraw the drone starting or ending point in its new position
            self.patch_manager.redraw_drone(self.selected_drone)

            self._update()
        ###########################################################################################
        # move the whole building patch
        elif self.selected_building and self.initial_click_position:
            ds = np.array(point) - np.array(self.initial_click_position)
            # Move the building
            # set the vertices of the src.Building object, then copy them into the building patch
            self.selected_building.move_building(ds)
            self.patch_manager.redraw_building(self.selected_building)
            # Update the initial click position for next movement calculation
            self.initial_click_position = point

            # Redraw to show the moved building
            self._update()

    def _on_button_release(self, event):
        self.initial_click_position = None
        self.selected_drone = None
        self.dragging_drone_point = None
        self.selected_vertex = None

    def _delete_selected_building(self):
        if self.selected_building:
            self.actions_stack.remove_action("building", self.selected_building)
            building = self.selected_building
            self.selected_building = None
            self.patch_manager.remove_building_patch(building)
            self.buildings.remove(building)
            self._update()

    def _on_key_press(self, event):
        # switch between building and drone placement modes
        self._switch_mode(event)

        if event.key == "tab" and self.mode == "building":
            # plot the building
            self._finalize_building()

        if event.key in ["z","cmd+z", "ctrl+z"]:
            self._undo_last_action()

        # if event.key in ["cmd+s", "ctrl+s"]:
        #     self._create_json(self.output_path)

        elif event.key in ["backspace", "delete"]:
            self._delete_selected_building()

        elif event.key == "escape":
            self._clear_temp_elements()

    def _show_warning(self, text: str, duration: float = 3, **kwargs) -> None:
        """Display the central warning temporarily, set kwargs as per ax.annotate"""
        self.warning.set_text(text)
        self.warning.set(**kwargs)
        self.warning.set_visible(True)  # Start with warning hidden
        self._update()
        # Set a timer to hide the warning after {duration} seconds
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
        self.timer = Timer(duration, self._hide_warning)
        self.timer.start()

    def _update(self):
        # draw the canvas again
        self.fig.canvas.draw()

    def _clear_temp_elements(self):

        self.patch_manager.remove_temp_drone_start()
        self.patch_manager.clear_building_vertices()

        self.current_drone = None
        self._update()

    def _undo_last_action(self):
        if not self.actions_stack.actions:
            return

        action, obj = self.actions_stack.retrieve_last_action()
        if action == "building":
            self.selected_building = None
            self.patch_manager.remove_building_patch(obj)

            self.buildings.remove(obj)

        elif action == "drone":
            if obj in self.drones:
                self.drones.remove(obj)
                self.patch_manager.remove_drone_patch(obj)

        self._update()

    def _switch_mode(self, event=None):
        """
        Switch between building and drone placement modes.
        If an event is provided and the key is 'd' or 'b', switch to the respective mode.
        If no event is provided, toggle between modes.
        """
        # If an event is provided, check the key and switch mode accordingly
        if event:
            if event.key == "d":
                new_mode = "drone"
            elif event.key == "b":
                new_mode = "building"
            else:
                # If the key is not 'd' or 'b', do not switch the mode
                return
        else:
            # No event provided, toggle the mode
            new_mode = "drone" if self.mode == "building" else "building"

        # Set the new mode and update the button label
        self.mode = new_mode
        switch_label = (
            "Switch to Buildings" if self.mode == "drone" else "Switch to Drones"
        )
        self.ui_components.rename_button(button_key="switch", new_label=switch_label)

        # Call the update method
        self._update()

    def _finalize_building(self):
        building = self.patch_manager.make_building()
        if building:
            # this if statement checks to see if a building was created
            # ie if the vertex number was >=3
            self.buildings.append(building)
            self.actions_stack.add_action("building", building)
            self._update()

    def _verify_path(self, path: str) -> bool:
        """Verify if path is a json file (existing or not) in a valid directory
        and show relevant warnings"""
        response = validate_json_path(path)
        result, info = response["result"], response["info"]
        if result != 0:
            self._show_warning(info, 3, color="g")
            return True
        else:
            self._show_warning(info, duration=3, color="r")
            return False

    def _text_box_submit(self, path: str):
        if self._verify_path(path):
            # set the new path and overwrite any previous warnings
            self._set_output_path(path, skip_check=True)

    def _load_json(self, path: str):
        """Checks validity of input json, shows relevant warnings and calls load_scene"""
        if not self._verify_path(path):
            return
        # first save the existing plot to temporary file
        create_json("TEMP.json", self.buildings, self.drones)
        try:
            self.load_scene(path)
            self._show_warning(
                f"Loaded {Path(path).resolve().name}", duration=3, color="g"
            )
        except FileNotFoundError as e:
            self._show_warning(f"Error: {path} does not exist.", 3, color="r")
            # TODO print full exception
            traceback.print_exc()
            # load back the temporary file
            self.load_scene("TEMP.json")
        except Exception as e:
            # not ideal but catch and json formatting errors for now
            self._show_warning(
                f"JSON Decode Error: {Path(path).resolve().name} format incompatible",
                3,
                color="r",
            )
            # TODO print full exception
            traceback.print_exc()
            # load back the temporary file
            self.load_scene("TEMP.json")

        os.remove("TEMP.json")

    def _create_json(self, path: str):
        if not self.drones:
            # amber warning for no drones
            self._show_warning(
                f"Saving scene to file: {path}\nWARNING, No Drones!",
                duration=3,
                color=(1, 0.75, 0, 1),
            )
        else:
            # green warning if at least one drone
            self._show_warning(f"Saving to file: \n{path}", duration=3, color="g")
        create_json(path, self.buildings, self.drones, self.HEIGHT)

    def _call(self, event: str, *args, **kwargs):
        """class called by observers triggered by button or text_box, see ui_components.py and observer_utils.py"""
        if event == "switch_mode":
            self._switch_mode()
        elif event == "reset":
            self._reset()
        elif event == "save":
            path = kwargs.get("input", self.output_path)
            self._set_output_path(path)
            self._create_json(path=path)
        elif event == "load_json":
            path = kwargs.get("input")
            self._load_json(path)
        elif event == "text_box_submit":
            path = kwargs["input"]
            self._text_box_submit(path)

    def _reset(self):
        self.selected_building = None
        self._clear_temp_elements()
        # Remove all building and drone patches
        self.patch_manager.clear_all()

        # Empty the buildings and drones lists
        self.buildings.clear()
        self.drones.clear()

        # Empty the actions stack
        self.actions_stack.clear()

        # Redraw the plot
        self.ax.figure.canvas.draw()


# if __name__ == "__main__":
#     # Example usage:
#     import runpy

#     # Replace 'module_name' with the name of your module
#     runpy.run_module('module_name', run_name='__main__')
#     plot = SceneBuilder()
#     plot.draw_scene()
#     # plot.draw_scene()

#     print("done")


# Suggestions:
# Save arena, just buildings, just drones etc
# better instructions
# vectors showing output of panel flow for each drone
# dragging buildings
# changing drone with click and drag
# change drone parameters such as source strength, imaginary source strength, goal strength, goal safety etc
# cooperating or not (can turn on and off for each drone)


# for status here:https://stackoverflow.com/questions/70842267/in-matplotlib-how-do-i-catch-that-event-zoom-tool-has-been-selected
