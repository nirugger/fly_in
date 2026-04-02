from __future__ import annotations
from src.zone import Zone
from src.connection import Connection
# if TYPE_CHECKING:


class Graph:
    def __init__(
            self,
            grid: dict[Zone, list[Connection]]
       ) -> None:

        self.grid = grid
        self._set_pois()

    def _set_pois(self) -> None:
        for item in self.grid.keys():
            if item.is_start:
                self.start = item
            if item.is_end:
                self.end = item

    def get_neighbors(self, zone: Zone) -> list[tuple[Zone, int]]:

        neighbors: list[tuple[Zone, int]] = []
        for item in self.grid.keys():
            if item.name == zone.name:
                for neighbor in self.grid[item]:
                    neighbors.append((
                        neighbor.get_other(item),
                        neighbor.get_other(item).movement_cost(),
                    ))
        return neighbors

    def get_pois(self) -> tuple[Zone, Zone]:
        return ((self.start, self.end))

    def __getitem__(self, key):
        return self.grid[key]

    def __setitem__(self, key, value):
        self.grid[key] = value
