"""Shared type definitions for the fly-in simulation.

All ``TypedDict`` classes used across parser, graph, and zone modules
are centralised here to avoid circular imports and to provide a single
source of truth for the shape of parsed data.
"""
from __future__ import annotations
from typing import TypedDict


class ZoneData(TypedDict):
    """Typed representation of a parsed zone entry.

    Attributes:
        line_num:   Source line number (for error reporting).
        name:       Unique zone identifier.
        type:       Zone type string: 'normal' | 'restricted' |
                    'priority' | 'blocked'.
        x:          X coordinate on the grid.
        y:          Y coordinate on the grid.
        max_drones: Maximum drones allowed simultaneously.
        color:      Display colour string (e.g. 'red', 'blue').
        is_start:   True if this is the start hub.
        is_end:     True if this is the end hub.
    """

    line_num: int
    name: str
    type: str
    x: int
    y: int
    max_drones: int
    color: str
    is_start: bool
    is_end: bool


class ConnectionData(TypedDict):
    """Typed representation of a parsed connection entry.

    Attributes:
        line_num:          Source line number (for error reporting).
        zone_a:            Name of the first zone endpoint.
        zone_b:            Name of the second zone endpoint.
        max_link_capacity: Maximum drones traversing simultaneously.
    """

    line_num: int
    zone_a: str
    zone_b: str
    max_link_capacity: int


class RawData(TypedDict):
    """Top-level typed dict returned by ``Parser.parse()``.

    Attributes:
        nb_drones:   Total number of drones in the simulation.
        zones:       Mapping of zone name to its ``ZoneData``.
        connections: Ordered list of ``ConnectionData`` entries.
    """

    nb_drones: int
    zones: dict[str, ZoneData]
    connections: list[ConnectionData]
