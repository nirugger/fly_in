from src.connection import Connection
from src.drone import Drone
from src.zone import Zone, ZoneType
from rendering.data import COLORS

import hashlib
import random


# da mettere in scheduler
def get_occupancy_at_turn(
        t: int,
        zone: Zone,
        drone_list: list[Drone],
        ) -> list[Drone]:
    """Return the list of drones currently occupying a zone.

    Args:
        zone (Zone): zone to inspect.

    Returns:
        list[Drone]: drones at the specified zone.
    """
    occupancy: list[Drone] = []
    for drone in drone_list:
        if zone is drone.position_at_turn(t):
            occupancy.append(drone)
    return occupancy


# da mettere in graph
def get_neighbors(
        zone: Zone,
        conn_list: list[Connection],
        ) -> list[Zone]:
    """Return rendered neighbor zones for a given zone.

    Args:
        zone (Zone): source zone to query.

    Returns:
        list[Zone]: list of adjacent zones.
    """
    neighbors = []
    for connection in conn_list:
        if connection.zone_a is zone:
            neighbors.append(connection.zone_b)
        elif connection.zone_b is zone:
            neighbors.append(connection.zone_a)

    return neighbors


def average_turn_per_drone(
        drone_list: list[Drone],
        current_t: int,
        previous_cost: int = 0,
        total: bool = False
        ) -> float:

    if current_t == 0:
        return 0

    if total:
        return sum(
            max(turn for turn, _ in drone.path)
            # - min(t for t, z in drone.path if not z.is_start)
            # + 1
            for drone in drone_list
        ) / len(drone_list)

    return sum(
        max(turn for turn, _ in drone.path if turn <= current_t)
        # - min(t for t, z in drone.path if not z.is_start)
        # + 1
        for drone in drone_list
    ) / len(drone_list)


def total_turn_cost(lst: list[Drone],
                    ot: int,
                    cc: int = 0
                    ) -> int:

    c: int = cc
    for d in lst:
        for t, z in d.path:
            if t == ot and z.is_start is False:
                c += z.movement_cost()
    return c


def compute_percentage(part: float, whole: float, decimals: int) -> float:
    """Return the completion percentage of the current simulation.

    Returns:
        float: percentage of current turn over maximum turn.
    """
    return round(part * 100 / whole, decimals)


def build_connection_path(path: list[Zone]) -> list[Connection]:
    conn_path: list[Connection] = []
    for i in range(0, len(path)):
        if i == len(path) - 1:
            break
        zone = path[i]
        next_zone = path[i + 1]
        if next_zone.zone_type is ZoneType.CONNECTION:
            next_zone = path[i + 2]
        conn: Connection | None = None
        for c in zone.connections:
            if c.zone_b is next_zone or c.zone_a is next_zone:
                conn = c
        if conn is None:
            continue
        conn_path.append(conn)
        i += 1
    return conn_path


def get_zone_color(zone: Zone) -> tuple[int, int, int]:
    """Resolve the display color for a zone.

    Args:
        zone (Zone): zone to color.

    Returns:
        tuple[int, int, int]: RGB color value.
    """
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
    """Generate a deterministic RGB color from a string.

    Args:
        string (str): input string to hash.

    Returns:
        tuple[int, int, int]: derived RGB color.
    """
    digested = hashlib.md5(string.encode()).digest()
    color = (digested[0], digested[1], digested[2])
    return color


def get_random_color() -> tuple[int, int, int]:
    return ((random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)))
