from scenebuilder.gui_sim import InteractivePlot

if __name__ == "__main__":
    # initialise the gui class
    p = InteractivePlot()
    # set a path relative to the terminal to save the scene
    p.set_output_path("examples/example2.json")
    # open the gui
    p.draw_scene()
