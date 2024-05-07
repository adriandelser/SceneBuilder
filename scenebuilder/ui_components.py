from __future__ import annotations

import matplotlib.pyplot as plt
from .observer_utils import Observable
from matplotlib.widgets import TextBox 


class UIComponents(Observable):
    def __init__(self, ax: plt.Axes):
        super().__init__()
        self.ax = ax
        self.fig = ax.figure
        button_y_val = 0.01
        self.buttons: dict[str, dict[str, plt.Axes | str | function]] = {
            "switch": {
                "axis": self.fig.add_axes([0.01, button_y_val, 0.20, 0.05]),
                "label": "Switch to Drones",
                "callback": self.on_switch_mode,
            },
            "reset": {
                "axis": self.fig.add_axes([0.22, button_y_val, 0.1, 0.05]),
                "label": "Reset",
                "callback": self.on_reset,
            },
            "create_json": {
                "axis": self.fig.add_axes([0.33, button_y_val, 0.15, 0.05]),
                "label": "Save JSON",
                "callback": self.on_json,
            },
            "load_json": {
                "axis": self.fig.add_axes([0.49, button_y_val, 0.15, 0.05]),
                "label": "Load JSON",
                "callback": self.on_load,
            },
        }

        # Initialize buttons and register callbacks
        for key, btn_info in self.buttons.items():
            button = plt.Button(btn_info["axis"], btn_info["label"])
            button.on_clicked(btn_info["callback"])
            self.buttons[key]["button"] = button

        #create textbox, color is (r,g,b,alpha)
        self.axbox = self.fig.add_axes([0.72, button_y_val, 0.2, 0.05])
        self.text_box = EnterTextBox(self.axbox, "Path:",
                                label_pad = 0.1, 
                                textalignment="left",
                                hovercolor=(0,1,0,0.2))
        
        self.text_box.on_submit(self.on_text_box)
        self.text_box.set_val("")
        self.fig.text(
                        0.1, 0.86, "Current output file: ", 
                        fontsize=10,  # Makes the font larger
                        fontweight='bold',  # Makes the font bold
                        color='k'  # Changes the text color
                        )
        self.current_file_text = self.fig.text(
                        0.32, 0.86, "scenebuilder.json", 
                        fontsize=10,  # Makes the font larger
                        fontweight='bold',  # Makes the font bold
                        color='g',  # Changes the text color
                        )


    # def submit(self, text: str) -> None:
    #     # self.notify_observers("evaluate", text)
    #     print(text)

    def rename_button(self, button_key: str, new_label: str) -> None:
        if button_key in self.buttons:
            self.buttons[button_key]["button"].label.set_text(new_label)
        else:
            raise ValueError(f"No button found with the key '{button_key}'")

    def modify_current_file_text(self, new_text: str) -> None:
        self.current_file_text.set_text(new_text)

    def on_switch_mode(self, event):
        self.notify_observers("switch_mode")

    def on_reset(self, event):
        self.notify_observers("reset")

    def on_json(self, event):
        self.notify_observers("create_json")

    def on_load(self,event):
        self.notify_observers("load_json", input = self.text_box.text)

    def on_text_box(self, text):
        self.text_box.stop_typing()
        self.notify_observers('text_box_submit', input=text)



class EnterTextBox(TextBox):

    def stop_typing(self, event=None):
        """
        By some magic, this method is enough to only submit the textbox when enter is pressed
        instead of both enter and clicking outside the textbox
        Override the default behavior to not submit when focus is lost.
        ie don't submit when clicking outside of the textbox,
        only submit if enter is pressed
        """
        self.capturekeystrokes = False
        self.cursor.set_visible(False)
        self.ax.figure.canvas.draw()
        

    
