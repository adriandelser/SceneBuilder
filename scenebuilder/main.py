import argparse
from scenebuilder import SceneBuilder


def main():
    parser = argparse.ArgumentParser(description="Launch the SceneBuilder GUI")

    parser.add_argument(
        "-l",
        "--load",
        type=str,
        help="Load a scene from a JSON file at the specified path",
    )

    args = parser.parse_args()

    app = SceneBuilder()

    loaded_file = None
    if args.load:
        app.load_scene(args.load)
        loaded_file = args.load

    intro_message = (
        "Welcome to the SceneBuilder! \n"
        "This is a tool for creating and editing a 2D scene with drones and buildings."
    )
    if loaded_file:
        intro_message += f"\nLoaded scene from file: {loaded_file}"
    app._show_warning(intro_message, duration=5, color="g")
    app.draw_scene()


if __name__ == "__main__":
    main()
