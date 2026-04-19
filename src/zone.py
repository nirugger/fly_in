"""Zone related module: Zone class and ZoneType enum."""
from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from src.drone import Drone
    from src.connection import Connection


class ZoneType(Enum):
    """Enum class for different Zone types.

    Args:
        Enum (_type_): parent Enum class.
    """

    NORMAL = "normal"          # cost: 1
    RESTRICTED = "restricted"  # cost: 2
    BLOCKED = "blocked"        # inaccessible
    PRIORITY = "priority"      # cost: 1, preferred by pathfinder
    CONNECTION = "connection"  # cost: 0


class Zone:
    """Represents a node in the drone routing network."""

    def __init__(
            self,
            name: str,
            zone_type: ZoneType,
            x: int,
            y: int,
            is_start: bool,
            is_end: bool,
            max_drones: int,
            color: str,
    ) -> None:
        """Init a Zone.

        Args:
            name (str): unique zone identifier.
            zone_type (ZoneType): ZoneType enum member.
            x (int): X coordinate on the grid.
            y (int): Y coordinate on the grid.
            is_start (bool): 'True' if this is the start hub.
            is_end (bool): 'True' if this is the end hub.
            max_drones (int): maximum simultaneous drones allowed.
            color (str): display colour string.
        """
        self.name = name
        self.zone_type = zone_type
        self.x = x
        self.y = y
        self.is_start = is_start
        self.is_end = is_end
        self.max_drones = max_drones
        self.color = color
        self.connections: list[Connection] = []
        self.current_drones: list[Drone] = []
        self.residual = max_drones
        self.prev: Zone | None = None

    def movement_cost(self) -> int:
        """Return the turn cost to move into this zone.

        Returns:
            int: 2 for RESTRICTED zones, 1 for all others.
        """
        cost: int = 1
        if self.zone_type is ZoneType.RESTRICTED:
            cost = 2
        if self.zone_type is ZoneType.CONNECTION:
            cost = 0
        return cost

    def is_accessible(self) -> bool:
        """Ask if Zone is not 'blocked'.

        Returns:
            bool: 'True' if Zone is not 'blocked'.
            bool: 'False' if Zone is 'blocked'.
        """
        return self.zone_type is not ZoneType.BLOCKED

    def has_priority(self) -> bool:
        """Ask if Zone is 'priority'.

        Returns:
            bool: 'True' if Zone is 'priority'.
            bool: 'False' if Zone is not 'priority'.
        """
        return self.zone_type is ZoneType.PRIORITY

    def has_capacity(self) -> bool:
        """Ask if there is space for a Drone to enter.

        Returns:
            'True' if Zone has space.
            'False' if Zone is full.
        """
        return len(self.current_drones) < self.max_drones

    def add_drone(self, drone: Drone) -> None:
        """Add a Drone to the Zone.

        Args:
            drone (Drone): the Drone to be added.
        """
        self.current_drones.append(drone)

    def remove_drone(self, drone: Drone) -> None:
        """Remove a Drone from the Zone.

        Args:
            drone (Drone): the Drone to be removed.
        """
        self.current_drones.remove(drone)

    def __str__(self) -> str:
        """Get the name of the Zone.

        Returns:
            str: the name of the Zone.
        """
        return self.name

    def __repr__(self) -> str:
        """Another getter of the name of the Zone.

        Returns:
            str: the name of the Zone.
        """
        return self.__str__()
