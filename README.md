# SceneBuilder

## Overview

**SceneBuilder** is a Python package that provides a Matplotlib-based GUI for designing 2D test environments in a 10x10m grid for use in multiagent path planning algorithms. Users can draw polygons to represent obstacles and arrows to indicate the starting and ending points of each agent's path.

<!-- ![Scene Example 1](/assets/scene1.png){width=10 height=10} -->
<p align="center">
  <img src="/assets/scene1.png" alt="First Image" width="40%" />
  <img src="/assets/scene2.png" alt="Second Image" width="40%" />
</p>

## Installation

To install SceneBuilder, run the following command:

```bash
pip install scenebuilder
```

This command installs SceneBuilder along with numpy and matplotlib, ensuring that everything needed to run the GUI is properly set up.




## Prerequisites

SceneBuilder's prerequisites are defined in the pyproject.toml file and include Matplotlib and numpy.

## Quick Start Guide

### Using Command-Line Options

You can use SceneBuilder directly from the command line with the following options:

- `-o`, `--output`: Specify the path where the scene should be saved as a JSON file.
- `-l`, `--load`: Specify a JSON file path to load an existing scene.

Example usage:

```bash
scenebuilder --load path/to/scene.json --output path/to/output.json
```

### In Code
To use SceneBuilder in code, you need to create an instance of the `SceneBuilder` class and invoke the `draw_scene()` method. Below is a simple example to get you started:

```python
from scenebuilder import SceneBuilder

# Create an instance of the SceneBuilder
scene = SceneBuilder()

# Open the GUI to draw a scene
scene.draw_scene()
```

Load in an existing compatible json file for modification:

```python
scene.load_scene("path/to/your_file.json")
scene.draw_scene()
```

Specify the path to save your output json to:

```python
scene.set_output_path("path/to/output.json")
scene.draw_scene()
```



## Features

- **Draw Obstacles**: Click within the GUI to place vertices of polygons that represent obstacles. Press Tab to complete an obstacle.
- **Add new obstacle vertices**: To add new vertices, click somewhere on the polygon's perimeter and drag to move the vertex to its desired location.
- **Set Drone Paths**: Click once to place the starting point, and again to place the goal of an agent/drone. An arrow will automatically be drawn from start to goal.
- **Move or adjust existing obstacles/drones**: Obstacles and drones can be moved by clicking and dragging. Drone start and goal points, as well as existing obstacle vertices can be moved in the same way.
- **Switch between Obstacle and Drone Modes**: Press b to switch to building/obstacle mode. Press d to switch to drone/agent mode. Alternatively click the Switch button on the bottom left of the gui.
- **Delete obstacles**: Select the obstacle and press delete or backspace. NOTE this is not yet available for drones.
- **Remove unwanted points**: To remove unwanted points (either obstacle vertices or a drone start point), press escape.
- **Undo drone/obstacle placement**: To remove the last obstacle or drone, press ctrl+z.
- **Reset Scene**: To reset the scene to a blank canvas, click the Reset button in the gui.

## Saving Scenes

Once you have created a scene, you can save it to a JSON file by clicking the 'Create JSON' button in the GUI. This file can then be used as input for path planning algorithms that require predefined scenes with obstacles and paths.

**_Unless otherwise specified, the file is saved as "scenebuilder.json" in the current working directory._**

## Contributing

Contributions to SceneBuilder are welcome! If you have suggestions for improvements or new features, feel free to create an issue or pull request on our GitHub repository.
