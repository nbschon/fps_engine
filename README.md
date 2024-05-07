# fps_engine

An FPS engine in the style of '90s shooters, like Doom and Duke Nukem.

This project will be using WebGPU via the `wgpu` crate for graphics, rather than a software renderer.

# Features
As of right now, you can generate a level with the included level editor, walk around, and collide
with walls in the way one would expect from a traditional first person game. The camera is fully 3D,
and the player can look in whichever direction they want -- it isn't limited to just yaw.

# Requirements
For the level editor (and subsequently, the engine itself) to work, Python Arcade needs to be installed.

# Level Editor Controls
- S
  - Change scaling of exported level (1.0x, 1.25x, 1.5x, 1.75x, 2.0x)
- C
  - Clear everything
- Alt / Option + C
  - Clear all walls
- Ctrl / Cmd + C
  - Clear all points
- Ctrl / Cmd + Z
  - Undo last wall / point placement
- Ctrl / Cmd + S
  - Saves level to `./level.json`
- Ctrl / Cmd + O
  - Opens level saved at `./level.json`
- Ctrl / Cmd + Q
  - Quit the editor
- Left Click on empty space
  - Add new point
- Left Click on point
  - Select as left side of wall
- Left Click on point (while left is selected)
  - Add new wall
- Alt / Option + Left Click
  - Set spawn position
- Ctrl / Cmd + Left Click on point
  - Delete point
- Right Click
  - Deselect point

# Engine Controls
- Escape / Q
  - Quit engine
- W / S
  - Move forward / backward
- A / D
  - Strafe left / right
- Move mouse cursor
  - Look around

# References
The main references I used:
- [Learn Wgpu Tutorial](https://sotrh.github.io/learn-wgpu/#what-is-wgpu)
- [Paul's Online Math Notes](https://tutorial.math.lamar.edu/classes/calciii/eqnsofplanes.aspx)
- [Orthogonal Projection](https://math.libretexts.org/Bookshelves/Linear_Algebra/Interactive_Linear_Algebra_(Margalit_and_Rabinoff)/06%3A_Orthogonality/6.03%3A_Orthogonal_Projection)

Most of the other code came from me hacking bits together and my own knowledge of trig.