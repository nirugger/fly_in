"""Drone class module.

Each Drone has a unique ID and a list of action per turn.
"""

from __future__ import annotations


class Drone:
    """Drone class."""

    def __init__(
            self,
            drone_id: int,
            start_zone: str
    ) -> None:
        """Init a Drone.

        Args:
            drone_id (int): identification number of the Drone.
            start_zone (str): the starting Zone of the Graph.
        """
        self.drone_id = drone_id
        self.path: list[tuple[str, int]] = [(start_zone, 0)]

    def position_at_turn(self, t: int) -> str | None:
        """Ask in which Zone will the Drone be in a given turn.

        Args:
            t (int): the given turn.

        Returns:
            str | None: Zone name at turn t | None if 'turn' not in path.
        """
        for pos, turn in self.path:
            if turn == t:
                return pos
        return None

    def moved_at_turn(self, t: int) -> bool:
        """Ask if Drone has changed Zone from previous given turn.

        Args:
            t (int): the given turn.

        Returns:
            bool: 'True' if Drone has changed Zone
            bool: 'False if Drone hasn't.
        """
        if t == 0:
            return False
        prev = self.position_at_turn(t - 1)
        curr = self.position_at_turn(t)
        return prev != curr and curr is not None
