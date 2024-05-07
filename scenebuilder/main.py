import argparse
from scenebuilder import SceneBuilder

def main():
    parser = argparse.ArgumentParser(description="Launch the SceneBuilder GUI")
    parser.add_argument("-o", "--output", type=str, help="Set the output path for saving the scene as JSON")
    parser.add_argument("-l", "--load", type=str, help="Load a scene from a JSON file at the specified path")

    args = parser.parse_args()

    app = SceneBuilder()

    if args.load:
        app.load_scene(args.load)

    if args.output:
        app.set_output_path(args.output)
    
    app.draw_scene()

if __name__ == "__main__":
    main()
