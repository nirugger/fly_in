"""Graph module: holds the network of zones and connections."""

from __future__ import annotations
from src.zone import Zone, ZoneType
from src.connection import Connection
from src.drone import Drone
from src.types import RawData, RenderGrid


class Graph:
    """Adjacency-list graph of Zone (nodes) connected by Connection (edges)."""

    def __init__(
            self,
            finder_grid: dict[Zone, list[Connection]],
            render_grid: RenderGrid,
            drones: list[Drone],
            ) -> None:
        """Initialize the Graph.

        Args:
            finder_grid (dict[Zone, list[Connection]]): adjacency mapping.
            render_grid (RenderGrid): grid used for rendering.
            drones (list[Drone]): list of drones in the simulation.
        """
        self.finder_grid = finder_grid
        self.render_grid = render_grid
        self.drones = drones
        self._set_pois()

    @classmethod
    def build_graph(
            cls,
            raw_data: RawData
            ) -> "Graph":
        """Construct a Graph from parsed raw data.

        Args:
            raw_data (RawData): parsed configuration data.

        Returns:
            Graph: initialized graph ready for scheduling.
        """
        zone_dict: dict[str, Zone] = {}
        for item in raw_data["zones"].values():
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

        render_grid: RenderGrid = RenderGrid(
            zones=list(zone_dict.values()),
            connections=connections
        )

        render_grid.zones.extend(
            c.zone_c for c in render_grid.connections
            if c.zone_c is not None
        )

        finder_grid: dict[Zone, list[Connection]] = {
            zone: [conn for conn in connections
                   if (conn.zone_a is zone
                       or conn.zone_b is zone)
                   and conn.zone_a.zone_type is not ZoneType.BLOCKED
                   and conn.zone_b.zone_type is not ZoneType.BLOCKED]
            for zone in zone_dict.values()
            if zone.zone_type is not ZoneType.BLOCKED
        }

        drones: list[Drone] = [
            Drone(drone_id=i)
            for i in range(1, raw_data["nb_drones"] + 1)
        ]

        return cls(
            render_grid=render_grid,
            finder_grid=finder_grid,
            drones=drones
        )

    def _set_pois(self) -> None:
        """Locate and cache the start and end Zone references."""
        for zone in self.finder_grid:
            if zone.is_start:
                self.start = zone
            if zone.is_end:
                self.end = zone

    def get_vacant_connections(
            self,
            zone: Zone
            ) -> list[Connection]:
        """Return all available connections from a given zone.

        Args:
            zone (Zone): source zone for the search.

        Returns:
            list[Connection]: available connections with remaining capacity.
        """
        return [
            conn for conn in self.finder_grid[zone]
            if conn.residual > 0 and
            conn.get_other(zone).residual > 0
        ]

    def get_connection_from_zones(
            self,
            zone_a: Zone,
            zone_b: Zone
            ) -> Connection | None:
        """Return the connection object linking two zones.

        Args:
            zone_a (Zone): first endpoint.
            zone_b (Zone): second endpoint.

        Returns:
            Connection | None: the connecting edge or None when no direct
            connection exists.
        """
        if (zone_a.zone_type is ZoneType.CONNECTION
                or zone_b.zone_type is ZoneType.CONNECTION):
            return None

        for connection in self.finder_grid[zone_a]:
            if connection.get_other(zone_a) is zone_b:
                return connection

        return None

    def get_neighbors(
            self,
            zone: Zone
            ) -> list[tuple[Zone, int]]:
        """Get all reachable Zones from 'zone' and their movement cost.

        Args:
            zone (Zone): The Zone whose neighbours are requested.

        Returns:
            list[tuple[Zone, int]]: List of (neighbor_zone, movement_cost).
        """
        neighbors: list[tuple[Zone, int]] = []
        for conn in self.finder_grid.get(zone, []):
            neighbor = conn.get_other(zone)
            neighbors.append((neighbor, neighbor.movement_cost()))
        return neighbors

    def get_pois(self) -> tuple[Zone, Zone]:
        """Get the (start, end) Zone pair.

        Returns:
            tuple[Zone, Zone]: Tuple of (start_zone, end_zone).
        """
        return (self.start, self.end)

    def __getitem__(
            self,
            key: Zone
            ) -> list[Connection]:
        """Get all Connections connected with given Zone 'key'.

        Args:
            key (Zone): the given Zone.

        Returns:
            list[Connection]: all Connection connected with 'key'.
        """
        return self.finder_grid[key]

    def __setitem__(
            self,
            key: Zone,
            value: list[Connection]
            ) -> None:
        """Add a 'Zone: list[Connection]' item to the grid.

        Args:
            key (Zone): the 'key' of grid item.
            value (list[Connection]): the 'value' of grid item.
        """
        self.finder_grid[key] = value
