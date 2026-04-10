"""Connection class module.

Each Connection represents an edge of the graph.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.zone import Zone
    from src.drone import Drone


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
        self.turn_in_transit = 0 | 1
        self.max_link_capacity = max_link_capacity
        self.drones_in_transit: list[Drone] = []

    def has_capacity(self) -> bool:
        """Ask if there is space for a Drone to transit.

        Returns:
            'True' if Connection has space.
            'False' if Connection is full.
        """
        return len(self.drones_in_transit) < self.max_link_capacity

    def get_other(self, zone: Zone) -> Zone:
        """Return the Zone connected with 'zone' argument.

        Args:
            zone (Zone): the Zone connected by Connection.

        Returns:
            Zone: the Zone connected with 'zone' by Connection.
        """
        return self.zone_b if zone.name == self.zone_a.name else self.zone_a

    def movement_cost(self, to_zone: Zone) -> int:
        """Calculate movement cost for traversing this Connection.

        Args:
            to_zone (Zone): the Zone to where the connection starts.

        Returns:
            int: the turns needed to traversing the Connection.
        """
        return to_zone.movement_cost()

    def add_drone(self, drone: Drone) -> None:
        """Add a Drone to the Connection.

        Args:
            drone (Drone): the Drone to be added.
        """
        self.drones_in_transit.append(drone)

    def remove_drone(self, drone: Drone) -> None:
        """Remove a Drone from the Connection.

        Args:
            drone (Drone): the Drone to be removed.
        """
        self.drones_in_transit.remove(drone)
