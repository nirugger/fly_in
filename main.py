from parser import Parser
from src.zone import Zone
from src.drone import Drone
from src.graph import Graph
from src.pathfinder import Pathfinder
from src.scheduler import Scheduler
from rendering.renderer import Renderer
import pygame
from rendering.menu import Menu
from rendering.data import RESOLUTION
# import sys


class SimulationManager:

    def __init__(self) -> None:
        self.screen = pygame.display.set_mode(RESOLUTION, pygame.RESIZABLE)
        self.graph: Graph | None = None

    def run(self) -> None:

        while True:
            menu = Menu(self.screen)
            path_to_map = menu.run()
            parser = Parser(path_to_map)
            raw_data = parser.parse()
            self.graph = Graph.build(raw_data)

            pathfinder = Pathfinder(self.graph)
            scheduler = Scheduler(self.graph, pathfinder)
            scheduler.schedule_drones()

            self.print_output()
            renderer = Renderer(self.screen, self.graph)
            renderer.run()

    def print_output(self) -> None:

        if not self.graph:
            return

        drones = self.graph.drones
        turn_map = self._build_turn_map(drones)

        for _, drone_zone in turn_map.items():
            line = ""
            for drone, zone in drone_zone:
                if zone.is_start:
                    continue
                line += f"D{drone}-{zone.name} "
            print(line)
        print()

    def _build_turn_map(
            self, drones: list[Drone]
            ) -> dict[int, list[tuple[int, Zone]]]:

        max_turn = max(
            turn for drone in drones
            for turn, _ in drone.path
        )

        turn_map: dict[int, list[tuple[int, Zone]]] = {
            t: [(drone.drone_id, zone)
                for drone in drones for turn, zone in drone.path
                if turn == t]
            for t in range(1, max_turn + 1)
        }

        return turn_map


if __name__ == "__main__":

    # try:
    #     parser = Parser(parse_argv(sys.argv))
    #     raw_data = parser.parse()

    # except FileNotFoundError:
    #     print("[ERROR]: "
    #           "expected usage:\ninsert <map_name> or leave empty")
    #     sys.exit(1)

    pygame.init()
    simulator = SimulationManager()
    # simulator.print_output()
    simulator.run()
