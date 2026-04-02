from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.zone import Zone
    from src.drone import Drone


class Connection:

    def __init__(
            self,
            zone_a: Zone,
            zone_b: Zone,
            max_link_capacity: int,
       ) -> None:
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.turn_in_transit = 0 | 1
        self.max_link_capacity = max_link_capacity
        self.drones_in_transit: list[Drone] = []

    def has_capacity(self) -> bool:
        """Return 1 if zone has capacity, 0 if not."""
        return len(self.drones_in_transit) < self.max_link_capacity

    def get_other(self, zone: Zone) -> Zone:
        return self.zone_b if zone.name == self.zone_a.name else self.zone_a

    def movement_cost(self, to_zone: Zone) -> int:
        """Calculate movement cost for traversing this Connection.

        Arguments:
            to_zone: the Zone to where the connection starts.
        Returns:
            int: 2 if to_zone is RESTRICTED, 1 otherwise.
        """
        return to_zone.movement_cost()

    def add_drone(self, drone: Drone) -> None:
        """Add Drone obj to the list.

        Arguments:
            drone: the Drone to be added.
        """
        self.drones_in_transit.append(drone)

    def remove_drone(self, drone: Drone) -> None:
        """Remove Drone obj from the list.

        Arguments:
            drone: the Drone to be removed.
        """
        self.drones_in_transit.remove(drone)
