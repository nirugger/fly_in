from src.graph import Graph
from src.zone import Zone, ZoneType
from itertools import count
import heapq


class Pathfinder:

    def __init__(
            self,
            graph: Graph,
    ) -> None:
        self.graph = graph
        self.paths: list[tuple[list[Zone], int]] = []

    def dijkstra(
            self
    ) -> bool:

        counter = count()
        visited: list[Zone] = [self.graph.start]
        queue: list[tuple[int, int, Zone]] = []
        current: Zone = self.graph.start
        heapq.heappush(queue, (0, next(counter), self.graph.start))
        while queue:
            cost, _, current = heapq.heappop(queue)

            if current.is_end:
                break
            connections = self.graph.get_valid_connections(current)

            for conn in connections:
                if (conn.get_other(current).zone_type is ZoneType.PRIORITY
                        and conn.get_other(current) not in visited):
                    conn.get_other(current).prev = current
                    visited.append(conn.get_other(current))
                    heapq.heappush(
                        queue, (
                            cost + conn.movement_cost(current),
                            next(counter),
                            conn.get_other(current)
                        )
                    )

            for conn in connections:
                if (conn.get_other(current).zone_type is not ZoneType.PRIORITY
                        and conn.get_other(current) not in visited):
                    conn.get_other(current).prev = current
                    visited.append(conn.get_other(current))
                    heapq.heappush(
                        queue, (
                            cost + conn.movement_cost(current),
                            next(counter),
                            conn.get_other(current)
                        )
                    )
        if not current.is_end:
            return False

        path: list[Zone] = []
        if current.prev:
            while current:
                path.append(current)
                if current.zone_type is ZoneType.RESTRICTED:
                    path.append(next(
                        (edge for edge in self.graph.grid[current]
                         if edge.get_other(current) is current.prev), None
                    ).zone_in_connection)
                current = current.prev
        min_capacity = self.get_minimum_capacity(path)
        self.paths.append((path[::-1], min_capacity))

        return True

    def set_minimum_capacity(self, path_cap: tuple[list[Zone], int]) -> None:
        path, cap = path_cap
        for i in range(1, len(path) - 1):
            conn = self.graph.get_conn_from_zones(path[i], path[i + 1])
            if conn:
                conn.residual -= cap
            path[i].residual -= cap

    def get_minimum_capacity(self, path: list[Zone]) -> int:
        max_capacity = len(self.graph.drones)
        for i in range(len(path) - 1):
            conn = self.graph.get_conn_from_zones(path[i], path[i + 1])
            if path[i].max_drones < max_capacity:
                max_capacity = path[i].max_drones
            if conn and conn.max_link_capacity < max_capacity:
                max_capacity = conn.max_link_capacity
        return max_capacity

    def EK(self):
        while self.dijkstra():
            self.set_minimum_capacity(self.paths[-1])
            print("CIAO QUAGLIO'\n")
