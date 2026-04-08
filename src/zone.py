"""Zone related module: Zone class and ZoneType enum."""
from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from src.drone import Drone
    from src.connection import Connection


class ZoneType(Enum):
    """Enum class for different Zone types."""

    NORMAL = "normal"          # cost: 1
    RESTRICTED = "restricted"  # cost: 2
    BLOCKED = "blocked"        # inaccessible
    PRIORITY = "priority"      # cost: 1, preferred by pathfinder

    @classmethod
    def from_str(cls, value: str) -> "ZoneType":
        """Instantiate a ZoneType from its string value.

        Args:
            value: One of 'normal', 'restricted', 'blocked', 'priority'.

        Returns:
            The matching ZoneType member.

        Raises:
            ValueError: If *value* does not match any member.
        """
        try:
            return cls(value)
        except ValueError:
            valid = [m.value for m in cls]
            raise ValueError(
                f"Invalid zone type '{value}'. Expected one of {valid}."
            )


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
        """Initialise a Zone.

        Args:
            name:       Unique zone identifier.
            zone_type:  ZoneType enum member.
            x:          X coordinate on the grid.
            y:          Y coordinate on the grid.
            is_start:   True if this is the start hub.
            is_end:     True if this is the end hub.
            max_drones: Maximum simultaneous drones allowed.
            color:      Display colour string.
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

    def movement_cost(self) -> int:
        """Return the turn cost to move into this zone.

        Returns:
            2 for RESTRICTED zones, 1 for all others.
        """
        return 2 if self.zone_type is ZoneType.RESTRICTED else 1

    def is_accessible(self) -> bool:
        """Return True if drones may enter this zone.

        Returns:
            False for BLOCKED zones, True otherwise.
        """
        return self.zone_type is not ZoneType.BLOCKED

    def has_priority(self) -> bool:
        """Return True if this zone is a PRIORITY zone.

        Returns:
            True if zone_type is PRIORITY.
        """
        return self.zone_type is ZoneType.PRIORITY

    def has_capacity(self) -> bool:
        """Return True if the zone can accept at least one more drone.

        Returns:
            True if current occupancy is below max_drones.
        """
        return len(self.current_drones) < self.max_drones

    def add_drone(self, drone: Drone) -> None:
        """Add a drone to this zone's occupancy list.

        Args:
            drone: The Drone to add.
        """
        self.current_drones.append(drone)

    def remove_drone(self, drone: Drone) -> None:
        """Remove a drone from this zone's occupancy list.

        Args:
            drone: The Drone to remove.
        """
        self.current_drones.remove(drone)

    def __str__(self) -> str:
        return self.name
