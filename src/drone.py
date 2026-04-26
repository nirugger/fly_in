"""Drone class module.

Each Drone has a unique ID and a list of action per turn.
"""
from __future__ import annotations
from src.zone import Zone


class Drone:
    """Represents a single drone in the simulation."""

    def __init__(
            self,
            drone_id: int,
            ) -> None:
        """Initialize a Drone.

        Args:
            drone_id (int): identification number of the Drone.
        """
        self.drone_id = drone_id
        self.path: list[tuple[int, Zone]] = []
        self.path_cost: int = 0
        self.drones_in_zones: int = 1
        self.orbit_offset: float = 0
        self.max_orbit_reached: bool = False

    def position_at_turn(
            self,
            t: int
            ) -> Zone | None:
        """Return the zone occupied by the drone at a specific turn.

        Args:
            t (int): the turn number to query.

        Returns:
            Zone | None: Zone at turn t, or None if the drone is not scheduled
            at that turn.
        """
        for turn, pos in self.path:
            if turn == t:
                return pos
        return None

    def moved_at_turn(
            self,
            t: int
            ) -> bool:
        """Return whether the drone changed zone at the given turn.

        Args:
            t (int): the turn number to compare.

        Returns:
            bool: True when the drone moved between turn t-1 and turn t.
        """
        if t == 0:
            return False
        prev = self.position_at_turn(t - 1)
        curr = self.position_at_turn(t)
        return prev != curr and curr is not None
