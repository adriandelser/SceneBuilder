from __future__ import annotations

import matplotlib.pyplot as plt
from .observer_utils import Observable
from matplotlib.widgets import TextBox
from tkinter import Tk, filedialog
from pathlib import Path
import os

# Initialize Tkinter just once
root = Tk()
root.withdraw()  # Hide the main window


class UIComponents(Observable):
    def __init__(self, ax: plt.Axes):
        super().__init__()
        self.ax = ax
        self.fig = ax.figure
        #################BOTTOM BUTTONS#####################
        button_y_val = 0.01
        self.buttons: dict[str, dict[str, plt.Axes | str | function]] = {
            "switch": {
                "axis": self.fig.add_axes([0.65, button_y_val, 0.20, 0.05]),
                "label": "Switch to Drones",
                "callback": self.on_switch_mode,
            },
            "reset": {
                "axis": self.fig.add_axes([0.22, button_y_val, 0.1, 0.05]),
                "label": "Reset",
                "callback": self.on_reset,
            },
            "save": {
                "axis": self.fig.add_axes([0.33, button_y_val, 0.15, 0.05]),
                "label": "Save",
                "callback": self.show_format_options,
            },
            "load_json": {
                "axis": self.fig.add_axes([0.49, button_y_val, 0.15, 0.05]),
                "label": "Load",
                "callback": self.on_load,
            },
        }

        # Initialize buttons and register callbacks
        for key, btn_info in self.buttons.items():
            button = plt.Button(btn_info["axis"], btn_info["label"])
            button.on_clicked(btn_info["callback"])
            self.buttons[key]["button"] = button

        self.fig.canvas.mpl_connect("key_press_event", self._on_key_press)
        CustomTextBox = TextBox
        ################# RESIZE BOXES #####################
        # TextBox for setting x-axis limits
        self.axbox_xmin = self.fig.add_axes([0.1, 0.05, 0.05, 0.04])
        self.text_box_xmin = CustomTextBox(self.axbox_xmin, 'Xmin', initial='-5',textalignment="center")
        self.text_box_xmin.label.set_position((0.9, -0.5))  # Move label to be above the box


        self.axbox_xmax = self.fig.add_axes([0.9, 0.05, 0.05, 0.04])
        self.text_box_xmax = CustomTextBox(self.axbox_xmax, 'Xmax', initial='5',textalignment="center")
        self.text_box_xmax.label.set_position((0.9, -0.5))  # Move label to be above the box

        # TextBox for setting y-axis limits
        self.axbox_ymin = self.fig.add_axes([0.03, 0.1, 0.05, 0.04])
        self.text_box_ymin = CustomTextBox(self.axbox_ymin, 'Ymin', initial='-5',textalignment="center")
        self.text_box_ymin.label.set_position((0.9, -0.5))  # Move label to be above the box

        self.axbox_ymax = self.fig.add_axes([0.03, 0.85, 0.05, 0.04])
        self.text_box_ymax = CustomTextBox(self.axbox_ymax, 'Ymax', initial='5',textalignment="center")
        self.text_box_ymax.label.set_position((0.9, 1.5))  # Move label to be above the box

        
        # # Buttons for quickly adjusting the limits
        # self.axbutton_double = self.fig.add_axes([0.1, 0.15, 0.15, 0.05])
        # self.button_double = plt.Button(self.axbutton_double, 'Double')
        # self.axbutton_halve = self.fig.add_axes([0.3, 0.15, 0.15, 0.05])
        # self.button_halve = plt.Button(self.axbutton_halve, 'Halve')

        # Connect the event handlers
        self.text_box_xmin.on_submit(self.update_limits)
        self.text_box_xmax.on_submit(self.update_limits)
        self.text_box_ymin.on_submit(self.update_limits)
        self.text_box_ymax.on_submit(self.update_limits)
        # self.button_double.on_clicked(self.double_limits)
        # self.button_halve.on_clicked(self.halve_limits)


        #################INPUT TEXT BOX#####################
        # # create textbox, color is (r,g,b,alpha)
        # self.axbox = self.fig.add_axes([0.72, button_y_val, 0.2, 0.05])
        # self.text_box = EnterTextBox(
        #     self.axbox,
        #     "Path:",
        #     label_pad=0.1,
        #     textalignment="left",
        #     hovercolor=(0, 1, 0, 0.2),
        # )

        # self.text_box.on_submit(self.on_text_box)
        # self.text_box.set_val("")
        #################OUTPUT FILE INFO#####################
        # self.fig.text(
        #     0.1,
        #     0.86,
        #     "Current output file: ",
        #     fontsize=10,  # Makes the font larger
        #     fontweight="bold",  # Makes  the font bold
        #     color="k",  # Changes the text color
        # )

        # self.current_file_text = self.fig.text(
        #     0.32,
        #     0.86,
        #     "scenebuilder.json",
        #     fontsize=10,  # Makes the font larger
        #     fontweight="bold",  # Makes the font bold
        #     color="g",  # Changes the text color
        # )

        #################SAVE FORMAT BUTTONS#####################
        # Create buttons for different formats, initially hidden
        formats = ["Default JSON", "GeoJSON", "Cancel"]
        self.format_buttons = []
        y_pos = 0.6  # Start position for the first format button
        for fmt in formats:
            ax_fmt = self.fig.add_axes([0.1, y_pos, 0.25, 0.1])
            btn = plt.Button(ax_fmt, fmt)
            btn.on_clicked(
                lambda event, fmt=fmt: self.on_save(fmt)
            )  # Pass fmt as a default value to the lambda
            self.format_buttons.append(btn)
            btn.ax.set_visible(False)
            btn.set_active(False)
            y_pos -= 0.12  # Adjust y position for the next button

    def rename_button(self, button_key: str, new_label: str) -> None:
        if button_key in self.buttons:
            self.buttons[button_key]["button"].label.set_text(new_label)
        else:
            raise ValueError(f"No button found with the key '{button_key}'")

    def show_format_options(self, event):
        # Make the format buttons visible and reposition them centered on the main plot
        center_x = self.ax.get_position().x0 + self.ax.get_position().width / 2
        center_y = self.ax.get_position().y0 + self.ax.get_position().height / 2
        button_width = 0.15
        button_height = 0.05
        num_buttons = len(self.format_buttons)
        total_height = num_buttons * button_height
        start_y = center_y + total_height / 2

        for i, btn in enumerate(self.format_buttons):
            ax_position = [
                center_x - button_width / 2,
                start_y - i * button_height,
                button_width,
                button_height,
            ]
            btn.ax.set_position(ax_position)
            btn.ax.set_visible(True)
            btn.set_active(True)

        plt.draw()  # Redraw the figure to update the visibility changes

    def update_limits(self, _):
        try:
            xmin = float(self.text_box_xmin.text)
            xmax = float(self.text_box_xmax.text)
            ymin = float(self.text_box_ymin.text)
            ymax = float(self.text_box_ymax.text)
            self.ax.set_xlim(xmin, xmax)
            self.ax.set_ylim(ymin, ymax)
            self.fig.canvas.draw_idle()
        except ValueError:
            print("Invalid input, please enter numerical values.")

    def on_switch_mode(self, event):
        self.notify_observers("switch_mode")

    def on_reset(self, event):
        self.notify_observers("reset")

    def on_save(self, format: str):
        for i, btn in enumerate(self.format_buttons):
            btn.ax.set_visible(False)
            btn.set_active(False)
        plt.draw()
        # do nothing if cancelled
        if format == "Cancel":
            return
        # set default extension
        if format == "Default JSON":
            extension = ".json"
        elif format == "GeoJSON":
            extension = ".geojson"

        # Get the current working directory
        current_directory = os.getcwd()
        filename = filedialog.asksaveasfilename(
            initialdir=current_directory,
            initialfile="scenebuilder",
            defaultextension=extension,
        )
        if not filename:
            return

        self.notify_observers("save", input=filename)

    def on_load(self, event):
        # Get the current working directory
        current_directory = os.getcwd()
        filename = filedialog.askopenfilename(initialdir=current_directory)
        if not filename:
            return
        filepath = str(Path(filename))
        self.notify_observers("load_json", input=filepath)

    def on_text_box(self, text):
        """NOTE Unused function for now"""
        self.text_box.stop_typing()
        self.notify_observers("text_box_submit", input=text)

    def _on_key_press(self, event):
        if event.key in ["cmd+s", "ctrl+s"]:
            self.show_format_options(event)


class CustomTextBox(TextBox):
    '''Same as normal textbox except overriding the _keypress method to call self.stop_typing
    when enter is pressed so that the textbox is deactivated'''
    def _keypress(self, event):
        if self.ignore(event):
            return
        if self.capturekeystrokes:
            key = event.key
            text = self.text
            if len(key) == 1:
                text = (text[:self.cursor_index] + key +
                        text[self.cursor_index:])
                self.cursor_index += 1
            elif key == "right":
                if self.cursor_index != len(text):
                    self.cursor_index += 1
            elif key == "left":
                if self.cursor_index != 0:
                    self.cursor_index -= 1
            elif key == "home":
                self.cursor_index = 0
            elif key == "end":
                self.cursor_index = len(text)
            elif key == "backspace":
                if self.cursor_index != 0:
                    text = (text[:self.cursor_index - 1] +
                            text[self.cursor_index:])
                    self.cursor_index -= 1
            elif key == "delete":
                if self.cursor_index != len(self.text):
                    text = (text[:self.cursor_index] +
                            text[self.cursor_index + 1:])
            self.text_disp.set_text(text)
            self._rendercursor()
            if self.eventson:
                self._observers.process('change', self.text)
                if key in ["enter", "return"]:
                    self.stop_typing()
                    self._observers.process('submit', self.text)

# NOTE currently unused, will be used for any potential user input
class EnterTextBox(TextBox):
    def stop_typing(self, event=None):
        """
        By some magic, this method is enough to only submit the textbox when enter is pressed
        instead of both enter and clicking outside the textbox.
        Override the default behavior to not submit when focus is lost.
        ie don't submit when clicking outside of the textbox,
        only submit if enter is pressed
        """
        self.capturekeystrokes = False
        self.cursor.set_visible(False)
        self.ax.figure.canvas.draw()
        print('stop_typing')
