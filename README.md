# SceneBuilder

## Overview

**SceneBuilder** is a Python package that provides a Matplotlib-based GUI for designing 2D test environments for use in multiagent path planning algorithms. Users can draw polygons to represent obstacles and arrows to indicate the starting and ending points of each agent's path.

<!-- ![Scene Example 1](/assets/scene1.png){width=10 height=10} -->
<p align="center">
  <img src="/assets/scene1.png" alt="Example Scene 1" width="40%" />
  <img src="/assets/scene2.png" alt="Example Scene 2" width="40%" />
</p>


## Installation

To install SceneBuilder, you have two options:

1. **Using pip (recommended)**:
   ```bash
   pip install scenebuilder
   ```

2. **From source**:
   ```bash
   git clone git@github.com:enac-drones/scenebuilder.git
   pip install -e .
   ```

## Prerequisites

SceneBuilder's prerequisites are defined in the pyproject.toml file and include Matplotlib and numpy.

## Quick Start Guide

### Using Command-Line Options

You can use SceneBuilder directly from the command line with the following option:

- `-l`, `--load`: Specify a JSON file path to load an existing scene.

Example usage:

```bash
scenebuilder --load path/to/scene.json
scenebuilder -l     path/to/scene.geojson
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

Alternatively, load in an existing compatible json file for modification:

```python
scene = SceneBuilder()
scene.load_scene("path/to/your_file.json")
scene.draw_scene()
```

## Features

- **Draw Obstacles**: Click within the GUI to place vertices of polygons that represent obstacles. Press Tab to complete an obstacle.
- **Add new obstacle vertices**: To add new vertices, click somewhere on the polygon's perimeter and drag to move the vertex to its desired location.
- **Set Drone Paths**: Click once to place the starting point, and again to place the goal of an agent/drone. An arrow will automatically be drawn from start to goal.
- **Move or adjust existing obstacles/drones**: Obstacles and drones can be moved by clicking and dragging. Drone start and goal points, as well as existing obstacle vertices can be moved in the same way.
- **Switch between Obstacle and Drone Modes**: Press b to switch to building/obstacle mode. Press d to switch to drone/agent mode. Alternatively click the Switch button on the bottom left of the gui.
- **Delete obstacles**: Select the obstacle and press delete or backspace. NOTE this is not yet available for drones.
- **Clear temporary points**: To clear building vertices prior to completing the building, or to remove a drone's starting point before placing the goal, press 'esc' or 'escape'.
- **Undo drone/obstacle placement**: To remove the last obstacle or drone that was placed, press z or ctrl+z. *
- **Reset Scene**: To reset the scene to a blank canvas, click the Reset button in the gui.

**_*Note: due to a quirk in tkinter, some standard keystrokes starting with ctrl/cmd are sometimes captured by the system instead of SceneBuilder, for this reason we provide the option to use them without the leading ctrl/cmd, for example "z" instead of "ctrl/cmd + z" for undo. This applies for the following commands usually found in the 'edit' dropdown menu on most systems:  <u>undo, redo, copy, paste, cut</u>_** **

**_**Not all of <u>undo, redo, copy, paste, cut</u> are currently implemented, this is a work in progress._**



## Saving Scenes

Once you have created a scene, you can save it to a JSON or GeoJSON file by clicking the 'Save' button in the GUI. You will then be prompted to select whether you want to use our basic JSON format or GeoGSON.

**_Unless otherwise specified, the file is saved as "scenebuilder.json" in the current working directory._**

## Contributing

Contributions to SceneBuilder are welcome! If you have suggestions for improvements or new features, feel free to create an issue or pull request on our GitHub repository.
