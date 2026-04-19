from src.graph import Graph
from src.zone import Zone, ZoneType


class Pathfinder:

    def __init__(
            self,
            graph: Graph
            ) -> None:

        self.graph = graph
        self.paths: list[tuple[list[Zone], int]] = []
        self.find_all_paths()

    def find_all_paths(
            self
            ) -> None:

        while self.next_shortest_path():
            self.update_max_capacity(self.paths[-1])
            print(self.paths[-1])
        if not self.paths:
            print("\nERROR: no path found\n")

    def insert_sorted(
            self,
            lst: list[tuple[int, Zone]],
            item: tuple[int, Zone]
            ) -> None:

        lst.append(item)
        lst.sort(
            key=lambda x: (
                x[0],
                0 if x[1].has_priority() else 1
            )
        )

    def update_max_capacity(
            self,
            path_capacity: tuple[list[Zone], int]
            ) -> None:
        path, capacity = path_capacity

        for i in range(1, len(path) - 1):

            if path[i].zone_type is ZoneType.CONNECTION:
                continue

            next_valid_zone = path[i + 1]
            if next_valid_zone.zone_type is ZoneType.CONNECTION:
                next_valid_zone = path[i + 2]

            connection = self.graph.get_connection_from_zones(
                path[i], next_valid_zone
            )

            if connection:
                connection.residual -= capacity
            if not path[i].is_start and not path[i].is_end:
                path[i].residual -= capacity

    def get_path_capacity(
            self,
            path: list[Zone]
            ) -> int:

        max_capacity = len(self.graph.drones)
        for i in range(len(path) - 1):
            connection = self.graph.get_connection_from_zones(
                path[i], path[i + 1]
            )
            if path[i].max_drones < max_capacity:
                max_capacity = path[i].max_drones
            if connection and connection.max_link_capacity < max_capacity:
                max_capacity = connection.max_link_capacity
        return max_capacity

    def next_shortest_path(
            self
            ) -> bool:

        for zone in self.graph.grid:
            zone.prev = None

        current: Zone = self.graph.start
        visited: list[Zone] = [current]
        priority_queue: list[tuple[int, Zone]] = [(0, current)]

        while priority_queue:
            cost, current = priority_queue.pop(0)

            if current.is_end:
                break

            connections = self.graph.get_vacant_connections(current)
            for connection in connections:
                other = connection.get_other(current)
                if other not in visited:
                    other.prev = current
                    visited.append(other)
                    self.insert_sorted(
                        priority_queue,
                        (cost + connection.movement_cost(current), other)
                    )

        if not current.is_end:
            return False

        path: list[Zone] = []
        if current.prev:
            while current:
                path.append(current)
                if current.zone_type is ZoneType.RESTRICTED:
                    connection_zone = next(
                        connection.zone_c
                        for connection in self.graph.grid[current]
                        if connection.get_other(current) is current.prev
                    )
                    path.append(connection_zone)
                current = current.prev

        self.paths.append(
            (path[::-1], self.get_path_capacity(path))
        )

        return True
