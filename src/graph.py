from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.zone import Zone
    from src.connection import Connection


class Graph:
    def __init__(
            self,
            raw_data: dict[str,
                           int
                           | dict[str, dict[str, str | int]]
                           | list[dict[str, str | int]]]
       ) -> None:

        self.grid: dict[Zone, list[Connection]] = self.init_grid(raw_data)
        self.zones: list[Zone] = self._init_zones(raw_data)
        self.connections: list[Connection] = self._init_connections(raw_data)
        self.start = self._find_start(self.zones)
        self.end = self._find_end(self.zones)

    def init_grid(
            self,
            raw_data: dict[str,
                           int
                           | dict[str, dict[str, str | int]]
                           | list[dict[str, str | int]]]
       ) -> None:
        pass

    def get_neighbors(self, zone: Zone) -> list[tuple[Zone, Connection]]:
        ...

    def get_connection(self, a: Zone, b: Zone) -> Connection | None:
        ...

    def __getitem__(self, key):
        return self.grid[key]

    def __setitem__(self, key, value):
        self.grid[key] = value