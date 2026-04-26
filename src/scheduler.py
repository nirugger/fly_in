"""Scheduler module for assigning paths to drones."""

from src.pathfinder import Pathfinder
from src.graph import Graph
from src.drone import Drone
from src.zone import Zone


class Scheduler:
    """Assigns computed paths to drones in the simulation."""

    def __init__(
            self,
            graph: Graph,
            pathfinder: Pathfinder
            ) -> None:
        """Initialize the scheduler.

        Args:
            graph (Graph): graph with zones and connections.
            pathfinder (Pathfinder): pathfinder instance containing paths.
        """
        self.graph = graph
        self.pathfinder = pathfinder
        self.unassigned_drones = [drone for drone in self.graph.drones]

    def assign_path(
            self,
            drone: Drone,
            path: list[Zone],
            turn: int,
            cost: int
            ) -> None:
        """Assign a path to a drone starting at a given turn.

        Args:
            drone (Drone): the drone to schedule.
            path (list[Zone]): ordered list of zones for the path.
            turn (int): turn at which the drone begins moving.
            cost (int): final path cost assigned to the drone.
        """
        for t in range(0, turn):
            drone.path.append((t, self.graph.start))

        for i, zone in enumerate(path[1:]):
            drone.path.append((i + turn, zone))

        drone.path_cost = cost

    def schedule_drones(self) -> None:
        """Schedule all drones across available paths.

        The scheduler assigns drones to sorted paths while respecting
        capacity constraints and turn offsets.
        """
        shortest_path = self.pathfinder.paths[0]
        min_cost = shortest_path['cost']
        min_cap = shortest_path['cap']

        turn = 1

        while self.unassigned_drones:
            for path_cap_cost in self.pathfinder.paths:
                current_path = path_cap_cost['path']
                current_cap = path_cap_cost['cap']
                current_cost = path_cap_cost['cost']
                if (current_cost >
                        min_cost + (len(self.unassigned_drones) // min_cap)):
                    break

                for _ in range(current_cap):
                    if self.unassigned_drones:
                        self.assign_path(
                            self.unassigned_drones.pop(0),
                            current_path,
                            turn,
                            current_cost
                        )

                if not self.unassigned_drones:
                    break
            turn += 1
