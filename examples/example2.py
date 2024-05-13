from scenebuilder import SceneBuilder

if __name__ == "__main__":
    # initialise the gui class
    p = SceneBuilder()
    # set a path relative to the terminal (or global path) to save the scene
    p._set_output_path("examples/example2.json")
    # open the gui
    p.draw_scene()
