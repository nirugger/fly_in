"""Graph module: holds the network of zones and connections."""

from __future__ import annotations
from src.zone import Zone, ZoneType
from src.connection import Connection
from src.drone import Drone
from src.types import RawData


class Graph:
    """Adjacency-list graph of Zone (nodes) connected by Connection (edges)."""

    def __init__(
            self,
            grid: dict[Zone, list[Connection]],
            drones: list[Drone],
    ) -> None:
        """Init a Graph.

        Args:
            grid: adjacency mapping Zone -> list of its Connections.
            drones: fleet of Drone for this simulation.
        """
        self.grid = grid
        self.drones = drones
        self._set_pois()

    @classmethod
    def build(cls, raw_data: RawData) -> "Graph":
        """Build a Graph and Drone fleet from the parser's output.

        Args:
            raw_data (RawData): all data needed for a Graph initialization.

        Returns:
            Graph: a fully initialized Graph instance.
        """
        zone_dict: dict[str, Zone] = {}
        start_zone_name: str = ""

        for item in raw_data["zones"].values():
            if item["type"] is ZoneType.BLOCKED:
                continue
            zone_dict[item["name"]] = Zone(
                name=item["name"],
                zone_type=item["type"],
                x=item["x"],
                y=item["y"],
                is_start=item["is_start"],
                is_end=item["is_end"],
                max_drones=item["max_drones"],
                color=item["color"],
            )
            if item["is_start"]:
                start_zone_name = item["name"]

        connections: list[Connection] = []
        for conn in raw_data["connections"]:
            zone_a = zone_dict.get(conn["zone_a"])
            zone_b = zone_dict.get(conn["zone_b"])
            if zone_a is None or zone_b is None:
                continue
            connections.append(Connection(
                zone_a=zone_a,
                zone_b=zone_b,
                max_link_capacity=conn["max_link_capacity"],
            ))

        grid: dict[Zone, list[Connection]] = {
            zone: [conn for conn in connections
                   if conn.zone_a is zone or conn.zone_b is zone]
            for zone in zone_dict.values()
        }

        drones: list[Drone] = [
            Drone(drone_id=i, start_zone=start_zone_name)
            for i in range(1, raw_data["nb_drones"] + 1)
        ]

        return cls(grid=grid, drones=drones)

    def _set_pois(self) -> None:
        """Locate and cache the start and end Zone references."""
        for zone in self.grid:
            if zone.is_start:
                self.start = zone
            if zone.is_end:
                self.end = zone

    def get_vacant_connections(
            self,
            zone: Zone
            ) -> list[Connection]:

        return [
            conn for conn in self.grid[zone]
            if conn.residual > 0 and
            conn.get_other(zone).residual > 0
        ]

    def get_connection_from_zones(
            self,
            zone_a: Zone,
            zone_b: Zone
            ) -> Connection | None:

        if (zone_a.zone_type is ZoneType.CONNECTION
                or zone_b.zone_type is ZoneType.CONNECTION):
            return None

        for connection in self.grid[zone_a]:
            if connection.get_other(zone_a) is zone_b:
                return connection

        return None

    def get_neighbors(self, zone: Zone) -> list[tuple[Zone, int]]:
        """Get all reachable Zones from 'zone' and their movement cost.

        Args:
            zone (Zone): The Zone whose neighbours are requested.

        Returns:
            list[tuple[Zone, int]]: List of (neighbor_zone, movement_cost).
        """
        neighbors: list[tuple[Zone, int]] = []
        for conn in self.grid.get(zone, []):
            neighbor = conn.get_other(zone)
            neighbors.append((neighbor, neighbor.movement_cost()))
        return neighbors

    def get_pois(self) -> tuple[Zone, Zone]:
        """Get the (start, end) Zone pair.

        Returns:
            tuple[Zone, Zone]: Tuple of (start_zone, end_zone).
        """
        return (self.start, self.end)

    def __getitem__(self, key: Zone) -> list[Connection]:
        """Get all Connections connected with given Zone 'key'.

        Args:
            key (Zone): the given Zone.

        Returns:
            list[Connection]: all Connection connected with 'key'.
        """
        return self.grid[key]

    def __setitem__(self, key: Zone, value: list[Connection]) -> None:
        """Add a 'Zone: list[Connection]' item to the grid.

        Args:
            key (Zone): the 'key' of grid item.
            value (list[Connection]): the 'value' of grid item.
        """
        self.grid[key] = value
