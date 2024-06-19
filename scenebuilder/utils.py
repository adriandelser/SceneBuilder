import numpy as np
from numpy.typing import ArrayLike

# from scenebuilder.json_utils import dump_to_json
from scenebuilder.entities import Drone, Obstacle

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


def get_case_from_dict(case: dict) -> tuple[list[Drone], list[Obstacle]]:
    """Get vehicles and building from json"""
    # get the first case in the dict
    case_info: dict = next(iter(case.values()))
    vehicles = case_info.get("vehicles")
    vehicles = [
        Drone(f"V{idx}", v["position"], v["goal"]) for idx, v in enumerate(vehicles)
    ]

    buildings = case_info.get("buildings")
    buildings = [Obstacle(np.array(b["vertices"])) for b in buildings]
    return vehicles, buildings


def create_json(path: str, buildings: list[Obstacle], drones: list[Drone], height:float=1.2) -> None:
    """Creates the json with the case info and writes it to file at path"""
    p = Path(path)
    # Convert path to absolute path for checking existence and permissions
    abs_path = p.resolve()
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
    # if abs_path extension is .json, do somethign
    dump_to_json(abs_path, c)
    if abs_path.suffix == ".geojson":
        c = convert_to_geojson(abs_path, "scenebuilder")
        dump_to_json(abs_path, c)


# this Class is not finished yet TODO
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()  # Convert numpy arrays to lists
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def validate_json_path(path: str, exit=False) -> dict:
    """Check if json input path is valid
    returns:
    0 if the path is invalid and/or if the file doesn't end in .json
    1 if the path is valid and ends in .json but does not exist
    2 if 1 but file exists

    system will quit if exit=True"""
    # Create a Path object
    p = Path(path)
    # Convert path to absolute path for checking existence and permissions
    abs_path = p.resolve()
    pathOK = 0

    if abs_path.is_dir():
        info = f"{abs_path} is a directory.\nPlease enter path ending with a .json file"
    # Check if the directory exists and is writable
    elif not abs_path.parent.exists() or not abs_path.parent.is_dir():
        info = (
            f"The directory '{abs_path.parent}' does not exist or is not a directory."
        )
    elif not os.access(abs_path.parent, os.W_OK):
        info = f"The directory '{abs_path.parent}' is not writable."
    # Check if the path ends with .json
    elif not path.endswith(".json") and not path.endswith(".geojson"):
        info = f"The file name '{abs_path.name}' must end with '.json' or '.geojson."
    elif not abs_path.exists():
        info = f"Warning:The file '{abs_path}' does not exist."
        pathOK = 1
    else:
        info = f"File {abs_path.name} exists"
        pathOK = 2

    if pathOK == 0 and exit:
        sys.exit(1)
    else:
        return {"result": pathOK, "info": info}


def convert_to_geojson(input_file: str, case_name: str):
    # Parse the JSON data
    data = load_from_json(input_file)
    geojson = {"type": "FeatureCollection", "features": []}

    # Process each building to convert it into a GeoJSON Polygon
    for building in data[case_name]["buildings"]:
        polygon = {
            "type": "Feature",
            "properties": {"ID": building["ID"], "type": "building"},
            "geometry": {"type": "Polygon", "coordinates": [[]]},
        }
        for vertex in building["vertices"]:
            # Assuming z-coordinate is not needed for the polygon display
            polygon["geometry"]["coordinates"][0].append([vertex[0], vertex[1]])

        # Ensure the polygon is closed (first vertex is the same as the last)
        if (
            polygon["geometry"]["coordinates"][0][0]
            != polygon["geometry"]["coordinates"][0][-1]
        ):
            polygon["geometry"]["coordinates"][0].append(
                polygon["geometry"]["coordinates"][0][0]
            )

        geojson["features"].append(polygon)

    # Process each vehicle to convert it into a GeoJSON LineString
    for vehicle in data[case_name]["vehicles"]:
        line = {
            "type": "Feature",
            "properties": {"ID": vehicle["ID"], "type": "vehicle"},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [
                        vehicle["position"][0],
                        vehicle["position"][1],
                    ],  # Starting coordinate
                    [vehicle["goal"][0], vehicle["goal"][1]],  # Ending coordinate
                ],
            },
        }
        geojson["features"].append(line)
    return geojson


def convert_from_geojson(geojson_input: str):
    # Parse the GeoJSON data
    geojson = load_from_json(geojson_input)

    original_format = {"scenebuilder": {"buildings": [], "vehicles": []}}

    # Process each feature in the GeoJSON
    for feature in geojson["features"]:
        if feature["geometry"]["type"] == "Polygon":
            # Assume it's a building
            building = {"ID": feature["properties"].get("ID"), "vertices": []}
            # Extract vertices; assume the first list in coordinates is the polygon ring
            for vertex in feature["geometry"]["coordinates"][0]:
                # Append vertices with a default z-coordinate since it's not in the GeoJSON
                building["vertices"].append(
                    vertex + [1.2]
                )  # Adding a default z-coordinate
            original_format["scenebuilder"]["buildings"].append(building)
        elif feature["geometry"]["type"] == "LineString":
            # Assume it's a vehicle
            vehicle = {
                "ID": feature["properties"].get("ID"),
                "position": feature["geometry"]["coordinates"][0]
                + [0.5],  # Adding a default z-coordinate
                "goal": feature["geometry"]["coordinates"][1]
                + [0.5],  # Adding a default z-coordinate
            }
            original_format["scenebuilder"]["vehicles"].append(vehicle)

    return original_format
