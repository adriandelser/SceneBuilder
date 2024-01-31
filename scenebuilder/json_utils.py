# file to store useful json utilities
import json, os


def load_from_json(file_path: str) -> dict:
    try:
        with open(file_path, "r") as f:
            file_contents = json.load(f)
            return file_contents
    except FileNotFoundError:
        # Create a new file if it doesn't exist
        with open(file_path, "x") as f:
            # Optionally, you can write some initial content to the file
            initial_data = {}
            json.dump(initial_data, f)
            return initial_data


def dump_to_json(file_path: str, data: dict) -> dict:
    # ensure the directory exists
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
        return None


# def to_json(self) -> dict:
#         """Converts the Case instance to a dictionary for JSON-style output. 
#         IMPORTANT: uses new json format with dicts instead of lists of buildings and vehicles"""

#         # buildings_data = [{["ID":building.ID,"vertices": building.vertices.tolist() for building in self.buildings]}]
#         buildings_data = []
#         for building in self.buildings:
#             building_dict = {"ID": building.ID, "vertices": building.vertices.tolist()}
#             buildings_data.append(building_dict)
#         vehicles_data = []
#         for vehicle in self.vehicle_list:
#             vehicle_dict = {"ID": vehicle.ID, 
#                             "position": vehicle.position.tolist(),
#                             "goal":vehicle.goal.tolist(),
#                             "source_strength":vehicle.source_strength,
#                             "imag_source_strength":vehicle.imag_source_strength,
#                             "sink_strength": vehicle.sink_strength
#                             }
#             vehicles_data.append(vehicle_dict)
#         # vehicles_data = {vehicle.ID:{'path': vehicle.path.tolist()} for vehicle in self.vehicle_list} if self.vehicle_list else []

#         case_data = {
#             self.name:
#             {'buildings': buildings_data,
#             'vehicles': vehicles_data}
#         }
        
#         return case_data
