from scenebuilder.gui_sim import InteractivePlot

if __name__ == "__main__":
    p =InteractivePlot()
    p.set_output_path('examples/scene.json')
    p.load_scene('examples/fake.json')
    p.draw_scene()