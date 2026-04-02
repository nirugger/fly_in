"""Zone related module, handle Zone datas, has utility methods."""
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
    BLOCKED = "blocked"        # cost: np.inf
    PRIORITY = "priority"      # cost: 1, has priority


class Zone:
    """Core Zone class"""
    def __init__(
            self,
            name: str,
            zone_type: ZoneType,
            x: int,
            y: int,
            is_start: bool,
            is_end: bool,
            max_drones: int,
            color: str | None,
       ) -> None:

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
        """Calculate movement cost for reaching this Zone.

        Returns:
            int: 2 if Zone is RESTRICTED, 1 otherwise.
        """
        return (self.zone_type == "restricted") + 1

    def is_accessible(self) -> bool:
        """Return 1 if zone is accessible, 0 if not."""
        return self.zone_type != "blocked"

    def has_priority(self) -> bool:
        """Return 1 if zone has priority, 0 if not."""
        return self.zone_type == "priority"

    def has_capacity(self) -> bool:
        """Return 1 if zone has capacity, 0 if not."""
        return len(self.current_drones) < self.max_drones

    def add_drone(self, drone: Drone) -> None:
        """Add Drone obj to the list.

        Arguments:
            drone: the Drone to be added.
        """
        self.current_drones.append(drone)

    def remove_drone(self, drone: Drone) -> None:
        """Remove Drone obj from the list.

        Arguments:
            drone: the Drone to be removed.
        """
        self.current_drones.remove(drone)

    def __str__(self):
        return self.name
