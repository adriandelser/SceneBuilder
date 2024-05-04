from __future__ import annotations

# from gui.gui_sim import InteractivePlot
import matplotlib.pyplot as plt
from scenebuilder.observer_utils import Observable


class UIComponents(Observable):
    def __init__(self, ax: plt.Axes):
        super().__init__()
        self.ax = ax
        self.fig = ax.figure
        self.buttons: dict[str, dict[str, plt.Axes | str | function]] = {
            "switch": {
                "axis": self.fig.add_axes([0.01, 0.01, 0.20, 0.05]),
                "label": "Switch to Drones",
                "callback": self.on_switch_mode,
            },
            # 'run': {
            #     'axis': self.fig.add_axes([0.22, 0.01, 0.1, 0.05]),
            #     'label': "Run",
            #     'callback': self.on_run
            # },
            "reset": {
                "axis": self.fig.add_axes([0.22, 0.01, 0.1, 0.05]),
                "label": "Reset",
                "callback": self.on_reset,
            },
            "create_json": {
                "axis": self.fig.add_axes([0.33, 0.01, 0.15, 0.05]),
                "label": "Create JSON",
                "callback": self.on_json,
            }  # ,
            # 'case_generate': {
            #     'axis': self.fig.add_axes([0.6, 0.01, 0.15, 0.05]),
            #     'label': "Generate Case",
            #     'callback': self.on_generate
            # }
        }

        # Initialize buttons and register callbacks
        for key, btn_info in self.buttons.items():
            button = plt.Button(btn_info["axis"], btn_info["label"])
            button.on_clicked(btn_info["callback"])
            self.buttons[key]["button"] = button

    def rename_button(self, button_key: str, new_label: str) -> None:
        if button_key in self.buttons:
            self.buttons[button_key]["button"].label.set_text(new_label)
        else:
            raise ValueError(f"No button found with the key '{button_key}'")

    def on_switch_mode(self, event):
        self.notify_observers("switch_mode")

    def on_reset(self, event):
        self.notify_observers("reset")

    # def on_run(self, event):
    #     self.notify_observers("run")

    def on_json(self, event):
        self.notify_observers("create_json")

    # def on_generate(self, event):
    #     self.notify_observers("generate_case")
