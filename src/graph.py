"""Graph module: holds the network of zones and connections."""
from __future__ import annotations
from typing import Any
from src.zone import Zone
from src.connection import Connection
from src.drone import Drone


class Graph:
    """Adjacency-list graph of Zone nodes connected by Connection edges.

    The canonical way to build a Graph from parsed map data is via the
    ``from_raw_data`` classmethod, which guarantees that every Zone and
    Connection object is created exactly once and shared consistently
    across the whole structure.
    """

    def __init__(
            self,
            grid: dict[Zone, list[Connection]],
            drones: list[Drone],
    ) -> None:
        """Initialise the graph.

        Args:
            grid:   Adjacency mapping Zone -> list of its Connections.
            drones: Fleet of Drone objects for this simulation.
        """
        self.grid = grid
        self.drones = drones
        self._set_pois()

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    @classmethod
    def from_raw_data(cls, raw_data: dict[str, Any]) -> "Graph":
        """Build a Graph (and drone fleet) from the parser's output.

        All Zone and Connection objects are created *once* here and
        reused everywhere, so identity checks and capacity tracking
        work correctly throughout the simulation.

        Args:
            raw_data: Dict produced by ``Parser.parse()`` with keys
                      ``nb_drones``, ``zones``, and ``connections``.

        Returns:
            A fully initialised Graph instance.
        """
        # 1. Build Zone registry (name -> Zone), skipping blocked zones.
        zone_registry: dict[str, Zone] = {}
        for item in raw_data["zones"].values():
            if item["type"] == "blocked":
                continue
            zone_registry[item["name"]] = Zone(
                name=item["name"],
                zone_type=item["type"],
                x=item["x"],
                y=item["y"],
                is_start=item["is_start"],
                is_end=item["is_end"],
                max_drones=item["max_drones"],
                color=item["color"],
            )

        # 2. Build Connection list using the *same* Zone objects.
        connections: list[Connection] = []
        for item in raw_data["connections"]:
            zone_a = zone_registry.get(item["zone_a"])
            zone_b = zone_registry.get(item["zone_b"])
            if zone_a is None or zone_b is None:
                # One endpoint is blocked/missing — skip silently.
                continue
            connections.append(Connection(
                zone_a=zone_a,
                zone_b=zone_b,
                max_link_capacity=item["max_link_capacity"],
            ))

        # 3. Build adjacency dict from the *same* Zone and Connection objects.
        grid: dict[Zone, list[Connection]] = {
            zone: [
                conn for conn in connections
                if conn.zone_a is zone or conn.zone_b is zone
            ]
            for zone in zone_registry.values()
        }

        # 4. Build drone fleet.
        drones: list[Drone] = [
            Drone(drone_id=i)
            for i in range(1, int(raw_data["nb_drones"]) + 1)
        ]

        return cls(grid=grid, drones=drones)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _set_pois(self) -> None:
        """Locate and cache the start and end Zone references."""
        for zone in self.grid:
            if zone.is_start:
                self.start = zone
            if zone.is_end:
                self.end = zone

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_neighbors(self, zone: Zone) -> list[tuple[Zone, int]]:
        """Return all zones reachable from *zone* and their movement cost.

        Args:
            zone: The Zone whose neighbours are requested.

        Returns:
            List of (neighbor_zone, movement_cost) tuples.
        """
        neighbors: list[tuple[Zone, int]] = []
        for conn in self.grid.get(zone, []):
            neighbor = conn.get_other(zone)
            neighbors.append((neighbor, neighbor.movement_cost()))
        return neighbors

    def get_pois(self) -> tuple[Zone, Zone]:
        """Return the (start, end) Zone pair.

        Returns:
            Tuple of (start_zone, end_zone).
        """
        return (self.start, self.end)

    def __getitem__(self, key: Zone) -> list[Connection]:
        return self.grid[key]

    def __setitem__(self, key: Zone, value: list[Connection]) -> None:
        self.grid[key] = value
