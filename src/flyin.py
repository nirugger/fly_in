"""Simulation launcher for the Fly In application.

This module starts the main simulation loop, manages the menu,
loads map data, builds the graph, schedules drones, and renders
simulation results.
"""

from parser import Parser

from src.graph import Graph
from src.pathfinder import Pathfinder
from src.scheduler import Scheduler
from src.output import write_output

from rendering.data import RESOLUTION
from rendering.menu import Menu, MenuState
from rendering.renderer import Renderer

import pygame

output_path: str = "output/"

map_registry: dict[str, str] = {
    'maps/easy/01_linear_path.txt': 'linear_path',
    'maps/easy/02_simple_fork.txt': 'simple_fork',
    'maps/easy/03_basic_capacity.txt': 'basic_capacity',
    'maps/medium/01_dead_end_trap.txt': 'dead_end_trap',
    'maps/medium/02_circular_loop.txt': 'circular_loop',
    'maps/medium/03_priority_puzzle.txt': 'priority_puzzle',
    'maps/hard/01_maze_nightmare.txt': 'maze_nightmare',
    'maps/hard/02_capacity_hell.txt': 'capacity_hell',
    'maps/hard/03_ultimate_challenge.txt': 'ultimate_challenge',
    'maps/challenger/01_the_impossible_dream.txt': 'the_impossible_dream',
    'maps/custom/01_custom_delta_v2.txt': 'river_delta',
    'maps/custom/02_feedback_loop_puzzle.txt': 'feedback_loop',
    'maps/custom/03_custom_highway.txt': 'highway_jam',
    'maps/custom/04_custom_labyrinth_city.txt': 'labyrinth_city',
    'maps/custom/00_a_day_off.txt': 'a_day_off'
}


class FlyInSimulator:
    """Manage the main simulation lifecycle.

    The manager forwards user selection to the parser, graph builder,
    pathfinder, scheduler, and renderer.
    """

    def __init__(self) -> None:
        """Initialize a FlyInSimulator."""
        self.screen = pygame.display.set_mode(RESOLUTION, pygame.RESIZABLE)
        self.graph: Graph | None = None
        self.new_run: bool = True

    def run(self) -> None:
        """Load a map and run the full simulation loop.

        The method displays the main menu, parses the selected map,
        builds the graph, schedules drones, and starts the renderer.
        """
        racondom_color = False
        while True:
            if self.new_run is True:
                menu = Menu(self.screen)
            path_to_map = menu.run(racondom_color)
            parser = Parser(path_to_map)
            raw_data = parser.parse()
            self.graph = Graph.build_graph(raw_data)

            pathfinder = Pathfinder(self.graph)
            if not pathfinder.paths:
                self.new_run = False
                menu.state = MenuState.INVALID_MAP
                continue
            else:
                self.new_run = True

            scheduler = Scheduler(self.graph, pathfinder)
            scheduler.schedule_drones()
            write_output(self.graph.drones, path_to_map)

            renderer = Renderer(self.screen, self.graph, pathfinder.paths)
            racondom_color = renderer.run()
