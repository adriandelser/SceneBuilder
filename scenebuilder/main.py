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

    if args.load:
        app.load_scene(args.load)

    app.draw_scene()


if __name__ == "__main__":
    main()
