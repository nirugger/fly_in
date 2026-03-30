from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.zone import Zone
    from src.connection import Connection


class Graph:
    def __init__(
            self,
            zones: dict[str, Zone],
            connections: list[Connection],
            _adjacency: dict[str, list[Connection]],
            start: Zone,
            end: Zone
       ) -> None:

    def get_neighbors(self, zone: Zone) -> list[tuple[Zone, Connection]]: ...
    def get_connection(self, a: Zone, b: Zone) -> Connection | None: ...