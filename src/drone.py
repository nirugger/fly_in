from __future__ import annotations


class Drone:

    def __init__(
            self,
            drone_id: int,
            start_zone: str
       ) -> None:

        self.drone_id = drone_id
        self.path: list[tuple[str, int]] = [(start_zone, 0)]

    def position_at_turn(self, t: int) -> str | None:
        """Return position at turn t, or None if already arrived."""
        for pos, turn in self.path:
            if turn == t:
                return pos
        return None

    def moved_at_turn(self, t: int) -> bool:
        if t == 0:
            return False
        prev = self.position_at_turn(t - 1)
        curr = self.position_at_turn(t)
        return prev != curr and curr is not None
