"""Shared type definitions for the fly-in simulation."""
from __future__ import annotations
from typing import TypedDict
from dataclasses import dataclass
from src.zone import Zone, ZoneType
from src.connection import Connection


class ZoneData(TypedDict):
    """Typed representation of a parsed zone entry.

    Args:
        TypedDict (_type_): partent TypedDict Class.

    Attributes:
        line_num (int): source line number for error reporting.
        name (str): unique zone identifier.
        type (ZoneType): ZoneType enum member.
        x (int): X coordinate on the grid.
        y (int): Y coordinate on the grid.
        max_drones (int): max drones allowed simultaneously.
        color (str): display colour string (e.g. 'red', 'blue').
        is_start (bool): 'True' if this is the start hub.
        is_end (bool): 'True' if this is the end hub.
    """

    line_num: int
    name: str
    type: ZoneType
    x: int
    y: int
    max_drones: int
    color: str
    is_start: bool
    is_end: bool


class ConnectionData(TypedDict):
    """Typed representation of a parsed connection entry.

    Args:
        TypedDict (_type_): parent TypedDict Class.

    Attributes:
        line_num: Source line number (for error reporting).
        zone_a: Name of the first zone endpoint.
        zone_b: Name of the second zone endpoint.
        max_link_capacity: Maximum drones traversing simultaneously.
    """

    line_num: int
    zone_a: str
    zone_b: str
    max_link_capacity: int


class RawData(TypedDict):
    """Top-level typed representation of a parsed configuration file.

    Args:
        TypedDict (_type_): parent TypedDict Class.

    Attributes:
        nb_drones: Total number of drones in the simulation.
        zones: Mapping of zone name to its 'ZoneData'.
        connections: Ordered list of 'ConnectionData' entries.
    """

    nb_drones: int
    zones: dict[str, ZoneData]
    connections: list[ConnectionData]


class Path(TypedDict):
    path: list[Zone]
    cap: int
    cost: int


@dataclass
class RenderGrid:
    zones: list[Zone]
    connections: list[Connection]
