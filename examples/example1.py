from scenebuilder.gui_sim import InteractivePlot

if __name__ == "__main__":
    # initialise the gui class
    p = InteractivePlot()
    # open the gui
    # note if create json is pressed in the gui,
    # a file called scenebuilder.json will be created in your working directory
    p.draw_scene()