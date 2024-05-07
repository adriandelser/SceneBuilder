import numpy as np
from numpy.typing import ArrayLike

# from scenebuilder.json_utils import dump_to_json
from .entities import Drone, Obstacle

# file to store useful json utilities
import json, os, sys
from pathlib import Path


def distance_between_points(p1: ArrayLike, p2: ArrayLike) -> float:
    """
    Returns the distance between two points.
    """
    p1, p2 = np.array(p1), np.array(p2)
    return np.linalg.norm(p1 - p2)


def load_from_json(file_path: str) -> dict:
    """Load json file contents into dict"""
    p = Path(file_path)
    file_path = p.resolve()
    with open(file_path, "r") as f:
        file_contents = json.load(f)
        return file_contents


def dump_to_json(file_path: str, data: dict) -> dict:
    """Write dict to json"""
    # ensure the directory exists
    p = Path(file_path)
    # Convert path to absolute path for checking existence and permissions
    file_path = p.resolve()
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
        return None


def get_from_json(case: dict) -> tuple[list[Drone], list[Obstacle]]:
    """Get vehicles and building from json"""
    case_info: dict = next(iter(case.values()))
    vehicles = case_info.get("vehicles")
    vehicles = [
        Drone(f"V{idx}", v["position"], v["goal"]) for idx, v in enumerate(vehicles)
    ]

    buildings = case_info.get("buildings")
    buildings = [Obstacle(np.array(b["vertices"])) for b in buildings]
    return vehicles, buildings


def create_json(path: str, buildings: list[Obstacle], drones: list[Drone]) -> None:
    """Creates the json with the case info and writes it to file at path"""
    p = Path(path)
    # Convert path to absolute path for checking existence and permissions
    abs_path = p.resolve()
    height = 1.2
    # this line adds a third dimension to the x,y coordinates of the building patches and creates a building object from each patch

    buildings = [
        {
            "ID": f"B{idx}",
            "vertices": np.hstack(
                [
                    building.vertices,
                    np.full((building.vertices.shape[0], 1), height),
                ]
            ).tolist(),
        }
        for idx, building in enumerate(buildings)
    ]

    vehicles = [
        {"ID": f"V{idx}", "position": v.position.tolist(), "goal": v.goal.tolist()}
        for idx, v in enumerate(drones)
    ]

    c = {"scenebuilder": {"buildings": buildings, "vehicles": vehicles}}
    dump_to_json(abs_path, c)


# this Class is not finished yet TODO
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()  # Convert numpy arrays to lists
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def validate_json_path(path:str, exit = False)->dict:
    '''Check if json input path is valid
    return True if valid, otherwise return False and quit if exit=True'''
    # Create a Path object
    p = Path(path)
    # Convert path to absolute path for checking existence and permissions
    abs_path = p.resolve()
    pathOK = True
    info = f'Path {abs_path} is valid'
    # Check if the path ends with .json
    if abs_path.is_dir():
        info = f"{abs_path} is a directory.\nPlease enter path ending with a .json file"
        pathOK = False
    elif not path.endswith(".json"):
        info = f"The file name '{abs_path.name}' must end with '.json'."
        pathOK=False
    # print(f"2:{abs_path.parent=}, {abs_path.parent.is_dir()}")

    # Check if the directory exists and is writable
    elif not abs_path.parent.exists() or not abs_path.parent.is_dir():
        info=f"The directory '{abs_path.parent}' does not exist or is not a directory."
        pathOK=False

    elif not os.access(abs_path.parent, os.W_OK):
        info = f"The directory '{abs_path.parent}' is not writable."
        pathOK=False

    if not exit:
        return {'result': pathOK, 'info': info}
    elif not pathOK:
        sys.exit(1)


    # If all checks are passed, confirm the path is valid
    # print(f"The path: {path} is valid.")
