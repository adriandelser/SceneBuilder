import numpy as np
from numpy.typing import ArrayLike


from gflow.cases import Case, Cases
from gflow.building import Building
from gflow.vehicle import Vehicle
from gflow.utils.simulation_utils import run_simulation
from gflow.utils.plot_utils import PlotTrajectories
from scenebuilder.entities import Drone, Obstacle


def distance_between_points(p1: ArrayLike, p2: ArrayLike) -> float:
    """
    Returns the distance between two points.
    """
    p1, p2 = np.array(p1), np.array(p2)
    return np.linalg.norm(p1 - p2)

#### TODO The methods below should potentially be removed from this project and lie in gflow or whichever path planning algorithm is being called
#### This project should just output the case, with the list of buildings and drones, and then the path planning algorithm should be called
#### This is just a temporary solution to get the gui working



def generate_case(name: str, buildings: list[Obstacle], drones: list[Drone]) -> Case:
    height = 1.2
    # this line adds a third dimension to the x,y coordinates of the building patches and creates a building object from each patch

    buildings = [ 
        Building(
            np.hstack(
                [
                    building.vertices,
                    np.full((building.vertices.shape[0], 1), height),
                ]
            )
        )
        for building in buildings
    ]


    # buildings = [Building(patch.get_xy()) for patch in self.building_patches]
    c = Case(name=name)
    c.buildings = buildings
    # c.vehicle_list = []
    c.vehicle_list = [
        Vehicle(ID=v.ID, source_strength=1, imag_source_strength=0.5) for v in drones
    ]
    for idx, d in enumerate(drones):
        c.vehicle_list[idx].Set_Position(d.position)
        c.vehicle_list[idx].Set_Goal(goal=d.goal, goal_strength=5, safety=None)
        c.vehicle_list[idx].Go_to_Goal(
            altitude=0.5, AoAsgn=0, t_start=0, Vinfmag=0
        )  # FIXME add these to the json
    generator = Cases(filename="gui_testing.json")
    generator.add_case(c)
    generator.update_json()

    complete_case = generator.get_case("gui_testing.json", name)
    complete_case.max_avoidance_distance = 3
    return complete_case


def run_case(case: Case):
    update_every = 1
    result = run_simulation(
        case,
        t=2000,
        update_every=update_every,
        stop_at_collision=False,
        max_avoidance_distance=case.max_avoidance_distance,
    )
    asdf = PlotTrajectories(case, update_every=update_every)
    # asdf = plt_utils.plot_trajectories(my_case) # Old plot

    asdf.show()
    return result
