*This project has been created as part of the 42 curriculum by nirugger.*

# Fly-In — Drone Routing Simulator

## Description

Fly-In is a drone routing simulation written in Python. The goal is to move a fleet of drones from a start hub to an end hub through a network of connected zones, in the fewest possible simulation turns.

The system parses a custom map format, builds an internal graph, computes optimal paths using a modified Dijkstra algorithm with residual capacity tracking, schedules drones across those paths, and renders the full simulation in an interactive graphical window powered by pygame.

---

## Instructions

### Requirements

- Python 3.10 or later
- [uv](https://github.com/astral-sh/uv) (package manager)

### Install dependencies

```bash
make install
```

### Run the simulator

```bash
make run
```

A graphical window will open with the main menu. From there you can navigate categories (Easy / Medium / Hard / Custom) and select any map to simulate.

### Debug mode

```bash
make debug
```

Runs the simulator under Python's built-in `pdb` debugger.

### Lint

```bash
make lint          # flake8 + mypy with standard flags
make lint-strict   # flake8 + mypy --strict + ruff
```

### Clean

```bash
make clean    # removes __pycache__, .mypy_cache, .ruff_cache
make fclean   # also removes output/, .cache/uv, .venv
```

### Simulation output

After each run, a text file is written to `output/<map_name>.txt` following the required format:

```
D1-roof1 D2-corridorA
D1-roof2 D2-tunnelB
D1-goal D2-goal
```

Each line represents one simulation turn. Drones that do not move are omitted. Drones that have reached the end zone are no longer tracked.

---

## Algorithm

### Overview

The routing pipeline consists of three stages: **Pathfinding → Scheduling → Rendering**.

### 1. Pathfinding — `src/pathfinder.py`

The pathfinder implements a **greedy successive shortest-path algorithm** with residual capacity tracking, inspired by the Ford-Fulkerson method adapted for multi-commodity routing.

**Steps:**

1. A modified **Dijkstra** traversal finds the shortest path from start to end in terms of turn cost, using a manually maintained priority list (no `heapq` or graph libraries).
2. `priority` zones are sorted ahead of `normal` zones at equal cost, making them preferred by the pathfinder.
3. The path's **bottleneck capacity** is computed as the minimum of all zone `max_drones` and connection `max_link_capacity` values along the route.
4. That capacity is subtracted from the **residual** of each zone and connection along the path.
5. The search restarts on the updated residual graph, finding the next viable path. This repeats until no path with remaining capacity exists.

This produces a list of paths sorted by length, each annotated with its capacity (`cap`) and turn cost (`cost`).

**Restricted zones** are handled by inserting a virtual intermediate `CONNECTION` zone between the source and the restricted destination. This intermediate zone represents the drone being in transit during the first of the two required turns, and it is tracked in both pathfinding and rendering.

**Complexity:** O(P × (V + E) log V), where P is the number of distinct paths found, V is the number of zones, and E is the number of connections. Paths are cached after discovery and reused by the scheduler.

### 2. Scheduling — `src/scheduler.py`

The scheduler assigns each drone to a pre-computed path with a **turn offset** to avoid congestion.

**Strategy:**

- Drones are dispatched in groups matching each path's capacity (`cap` drones per path per turn offset).
- The scheduler iterates over paths sorted by cost (shortest first), filling each path to its capacity before moving to the next.
- A path is only used if its cost does not exceed the shortest path cost by more than `len(remaining_drones) // min_cap` extra turns. This heuristic avoids routing drones down significantly longer detours when the bottleneck route can absorb them with a small queue delay.
- Each batch of drones on a path is staggered by one turn relative to the previous batch, ensuring no two drones collide at any zone or connection.

### 3. Graph — `src/graph.py`

The graph is represented as an **adjacency list**: `dict[Zone, list[Connection]]`. It holds two grids:

- `finder_grid`: used for pathfinding; excludes `BLOCKED` zones and their connections.
- `render_grid`: used for rendering; includes all zones and connections, plus virtual `CONNECTION` intermediate zones.

Blocked zones are excluded at build time, so the pathfinder never visits them.

### 4. Data model

| Class | Role |
|---|---|
| `Zone` | Graph node. Holds type, coordinates, capacity, residual. |
| `Connection` | Graph edge. Bidirectional, holds `max_link_capacity`, residual, and an optional virtual `zone_c` for restricted transit. |
| `Drone` | Holds its full scheduled path as a list of `(turn, Zone)` pairs. |
| `Graph` | Adjacency-list graph with start/end zone references. |
| `Pathfinder` | Computes and stores all viable paths. |
| `Scheduler` | Assigns paths and turn offsets to drones. |

---

## Visual Representation

The simulation is rendered using **pygame** with a custom graphical interface.

### Main menu

A navigable menu lets the user choose maps by category (Easy, Medium, Hard, Custom, Challenger) before launching the simulation.

### Simulation view

- **Zones** are drawn as circles, colored according to their `color` metadata or their `ZoneType` (restricted zones have a distinct hue, priority zones another).
- **Connections** are drawn as lines between zones. Intermediate virtual connection zones for restricted paths are also displayed.
- **Drones** are animated as small circles that move along their scheduled paths. Multiple drones sharing a zone are rendered in orbit around the zone center to avoid overlap.
- **Tooltips** appear on hover, showing zone name, type, capacity, and current occupancy.
- **HUD** displays the current turn number, total turns, and playback controls.

### Playback controls

| Key / Button | Action |
|---|---|
| Space | Play / Pause |
| ⬅ / ➡ | Step backward / forward one turn |
| ⬆ / ⬇ | Adjust animation speed |
| C | Change drone colors |
| Q | Quit the program |
| Escape | Return to the main menu |

### Fonts

The renderer uses bundled **JetBrains Mono** (Regular and Bold) for all text rendering, ensuring consistent display across platforms.

---

## Performance Benchmarks

| Map | Drones | Target | Result |
|---|---|---|---|
| Linear path (easy) | 2 | ≤ 6 | 4 |
| Simple fork (easy) | 3 | ≤ 6 | 4 |
| Basic capacity (easy) | 4 | ≤ 8 | 6 |
| Dead end trap (medium) | 5 | ≤ 15 | 8 |
| Circular loop (medium) | 6 | ≤ 20 | 11 |
| Priority puzzle (medium) | 4 | ≤ 12 | 7 |
| Maze nightmare (hard) | 8 | ≤ 45 | 14 |
| Capacity hell (hard) | 12 | ≤ 60 | 18 |
| Ultimate challenge (hard) | 15 | ≤ 35 | 26 |
| The Impossible Dream (challenger) | 25 | < 45 | 43 |


---

## Resources

### Graph algorithms & pathfinding

- [Dijkstra's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Ford-Fulkerson method — Wikipedia](https://en.wikipedia.org/wiki/Ford%E2%80%93Fulkerson_algorithm)
- [Successive shortest paths — Wikipedia](https://en.wikipedia.org/wiki/Successive_shortest_paths)
- [Multi-commodity flow problem — Wikipedia](https://en.wikipedia.org/wiki/Multi-commodity_flow_problem)


### Pygame

- [pygame documentation](https://www.pygame.org/docs/)

### AI usage

AI (Claude by Anthropic) was used during this project for the following tasks:

- **Project architecture**: setting up an initial project architecture completely object oriented.
- **Docstrings**: generating most of the dosctrings.
- **README drafting**: generating the initial structure and content of this file.


All AI-generated content was reviewed, tested, and validated before being included in the project. No code was copy-pasted from AI output without full understanding.

FYI, the line above was entirely written by AI without knowing if it was true or false, it just assumed it was true. Never trust the AI.
