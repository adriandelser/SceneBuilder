from scenebuilder import SceneBuilder

if __name__ == "__main__":
    # initialise the gui class
    p = SceneBuilder()
    # set a path relative to the terminal to save the scene
    p.set_output_path("examples/example3.json")
    # load from an existing compatible json file (global or relative path)
    p.load_scene("examples/example2.json")
    # open the gui
    p.draw_scene()
