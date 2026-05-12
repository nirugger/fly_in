"""Shared rendering helper functions for the Pygame renderer."""
from rendering.data import COLORS
from src.drone import Drone
from src.zone import Zone, ZoneType
from src.connection import Connection

import hashlib
import random


def get_occupancy_at_turn(
        t: int,
        zone: Zone,
        drone_list: list[Drone],
        ) -> list[Drone]:
    """Return the list of drones currently occupying a zone.

    Args:
        t (int): the turn of inspection.
        zone (Zone): zone to inspect.
        drone_list (list[Drone]): drones to check.

    Returns:
        list[Drone]: drones at the specified zone.
    """
    occupancy: list[Drone] = []
    for drone in drone_list:
        if zone is drone.position_at_turn(t):
            occupancy.append(drone)
    return occupancy


def average_turn_per_drone(
        drone_list: list[Drone],
        current_t: int,
        previous_cost: int = 0,
        total: bool = False
        ) -> float:
    """Compute the average number of turns per drone."""
    if current_t == 0:
        return 0

    if total:
        return sum(
            max(turn for turn, _ in drone.path)
            for drone in drone_list
        ) / len(drone_list)

    return sum(
        max(turn for turn, _ in drone.path if turn <= current_t)
        for drone in drone_list
    ) / len(drone_list)


def total_turn_cost(lst: list[Drone],
                    ot: int,
                    cc: int = 0
                    ) -> int:
    """Calculate the total movement cost for one turn."""
    c: int = cc
    for d in lst:
        for t, z in d.path:
            if t == ot and z.is_start is False:
                c += z.movement_cost()
    return c


def compute_percentage(part: float, whole: float, decimals: int) -> float:
    """Return the simulation completion percentage."""
    return round(part * 100 / whole, decimals)


def build_connection_path(z_path: list[Zone]) -> list[Connection]:
    """Build connection path from zone path."""
    c_path: list[Connection] = []
    if len(z_path) == 0:
        return c_path

    for i in range(0, len(z_path)):
        if i == len(z_path) - 1:
            break
        zone = z_path[i]
        next_zone = z_path[i + 1]
        if next_zone.zone_type is ZoneType.CONNECTION:
            next_zone = z_path[i + 2]
        conn: Connection | None = None
        for c in zone.connections:
            if c.zone_b is next_zone or c.zone_a is next_zone:
                conn = c
        if conn is None:
            continue
        c_path.append(conn)
        i += 1
    return c_path


def get_zone_color(zone: Zone) -> tuple[int, int, int]:
    """Resolve the display color for a zone."""
    string = zone.color
    if string == "None":
        return (210, 210, 215)

    if string == "rainbow":
        return get_random_color()

    color = COLORS.get(string)
    if color is None:
        color = get_color_from_string(string)
    return color


def get_color_from_string(string: str) -> tuple[int, int, int]:
    """Generate a deterministic RGB color from a string."""
    digested = hashlib.md5(string.encode()).digest()
    color = (digested[0], digested[1], digested[2])
    return color


def get_random_color() -> tuple[int, int, int]:
    """Return a random RGB color tuple."""
    return ((random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)))
