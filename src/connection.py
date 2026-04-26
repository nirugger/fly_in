"""Connection class module.

Each Connection represents an edge of the graph.
"""

from __future__ import annotations
from src.zone import Zone, ZoneType


class Connection:
    """Connection class."""

    def __init__(
            self,
            zone_a: Zone,
            zone_b: Zone,
            max_link_capacity: int,
            ) -> None:
        """Init a Connection.

        Args:
            zone_a (Zone): one of the two Zone connected by Connection.
            zone_b (Zone): one of the two Zone connected by Connection.
            max_link_capacity (int): max number of Drone in transit per turn.
        """
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.zone_c: Zone | None = None
        self.max_link_capacity = max_link_capacity
        self.residual = max_link_capacity
        self.name = f"{self.zone_a.name}-{self.zone_b.name}"
        self._init_zone_c()

    def _init_zone_c(self) -> None:
        """Initialize the intermediate connection zone for restricted edges."""
        if (self.zone_a.zone_type is ZoneType.RESTRICTED or
                self.zone_b.zone_type is ZoneType.RESTRICTED):
            self.zone_c = Zone(
                name=f"{self.zone_a.name}-{self.zone_b.name}",
                zone_type=ZoneType.CONNECTION,
                x=(self.zone_a.x + self.zone_b.x) // 2,
                y=(self.zone_a.y + self.zone_b.y) // 2,
                is_start=False,
                is_end=False,
                max_drones=self.max_link_capacity,
                color="None"
            )

    def get_other(
            self,
            zone: Zone
            ) -> Zone:
        """Return the Zone connected with 'zone' argument.

        Args:
            zone (Zone): the Zone connected by Connection.

        Returns:
            Zone: the Zone connected with 'zone' by Connection.
        """
        return self.zone_b if zone.name == self.zone_a.name else self.zone_a

    def movement_cost(
            self,
            from_zone: Zone
            ) -> int:
        """Calculate movement cost for traversing this Connection.

        Args:
            from_zone (Zone): the Zone from where the connection starts.

        Returns:
            int: the turns needed to traverse the Connection.
        """
        return self.get_other(from_zone).movement_cost()
