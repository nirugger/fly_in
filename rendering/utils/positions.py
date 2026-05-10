from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rendering.renderer import Renderer

from rendering.data import SPAN, ZONE_R
from rendering.utils.tools import get_occupancy_at_turn

from src.zone import Zone, ZoneType
from src.drone import Drone

import math


def update_drones_action_map(rend: Renderer) -> None:
    """Calculate drone state counts for the current turn.

    Returns:
        dict[str, int]: counts for waiting, prepping, moving, and
            arrived drones.
    """
    waiting: list[Drone] = []
    prepping: list[Drone] = []
    moving: list[Drone] = []
    arrived: list[Drone] = []

    for d in rend.drones:

        ptt = position_this_turn(rend, d)
        pnt = position_next_turn(rend, d)
        lnt = later_next_turn(rend, d)
        pat = d.position_at_turn(int(rend.current_turn))

        if rend.paused and rend.current_turn.is_integer():
            if pnt is None:
                arrived.append(d)
            elif pnt is ptt and lnt is ptt:
                waiting.append(d)
            elif (ptt is not pnt
                    and pat and not pat.is_end
                    and pat.zone_type is not ZoneType.CONNECTION):
                prepping.append(d)
            elif ptt is not pnt and pat and not pat.is_end:
                moving.append(d)

        else:
            if pnt is None:
                arrived.append(d)
            elif pnt is ptt and lnt is ptt:
                waiting.append(d)
            elif pnt is ptt and lnt is not ptt:
                prepping.append(d)
            elif ptt is not pnt and pat and not pat.is_end:
                moving.append(d)

    rend.drones_action_map = {
        'waiting': waiting,
        'prepping': prepping,
        'moving': moving,
        'arrived': arrived
    }


def update_angles_and_orbit(
        rend: Renderer,
        dt: float
        ) -> None:

    for drone in rend.drones:
        rend.drone_angles[drone.drone_id] += (
            rend.speed * dt * (15 / drone.drones_in_zones)
        )

    # if rend.orbit_maxxed is False and rend.speed != 0.0:
    #     rend.orbit_offset += 1
    # elif rend.orbit_maxxed is True and rend.speed != 0.0:
    #     rend.orbit_offset -= 1

    if rend.orbit_offset > SPAN or rend.orbit_offset < 0:
        rend.orbit_maxxed = not rend.orbit_maxxed


def reset_drones_sync(
        rend: Renderer,
        orbit: bool = True,
        angles: bool = True,
        zones: bool = True,
        o_flag: bool = False,
        orbit_offset: float = 0.0
        ) -> None:
    """Reset drone synchronization state for rendering.

    Args:
        orbit (bool): reset orbit offsets.
        angles (bool): reset drone rotation angles.
        zones (bool): reset per-zone occupancy counters.
    """

    if orbit is True:
        rend.orbit_offset = orbit_offset
        rend.orbit_maxxed = o_flag

    for drone in rend.drones:
        if angles is True:
            rend.drone_angles[drone.drone_id] = rend.speed * 0.016 * 2.5
        if zones is True:
            drone.drones_in_zones = 1


def get_drone_position(
        rend: Renderer,
        drone: Drone
        ) -> tuple[int, int] | None:
    """Compute the current screen position of a drone.

    Args:
        drone (Drone): drone to position.

    Returns:
        tuple[int, int] | None: screen coordinates or None if unavailable.
    """
    zone_a = position_this_turn(rend, drone)
    zone_b = position_next_turn(rend, drone)
    t = int(rend.current_turn)
    dt = rend.current_turn - t

    if zone_a is None or zone_b is None:
        return None

    zone_a_pos = rend.z_positions.get(zone_a)
    zone_b_pos = rend.z_positions.get(zone_b)

    if zone_a_pos is None or zone_b_pos is None:
        return None

    drones_in_zone = get_occupancy_at_turn(t, zone_a, rend.drones)

    if zone_a is zone_b:

        if later_next_turn(rend, drone) is zone_a:
            waiting_drones = [
                d for d in drones_in_zone
                if position_next_turn(rend, d) is zone_a
                and later_next_turn(rend, d) is zone_a
            ]

            for wd in waiting_drones:
                wd.drones_in_zones = len(waiting_drones)

            return calculate_orbit(
                rend=rend,
                drone=drone,
                drone_list=waiting_drones,
                center_x=zone_a_pos[0],
                center_y=zone_a_pos[1],
                mult=1.5 if len(waiting_drones) > 1 else 2.0,
                waiting=True,
                single=False if len(waiting_drones) > 1 else True
            )

        else:
            prepping_drones = [
                d for d in drones_in_zone
                if position_next_turn(rend, d) is zone_a
                and later_next_turn(rend, d) is not zone_a
            ]

            for pd in prepping_drones:
                pd.drones_in_zones = len(prepping_drones)

            if len(prepping_drones) == 1:
                return (zone_a_pos[0], zone_a_pos[1])
            return calculate_orbit(
                rend=rend,
                drone=drone,
                drone_list=prepping_drones,
                center_x=zone_a_pos[0],
                center_y=zone_a_pos[1],
                mult=0.6,
            )

    if (float(rend.current_turn).is_integer() and
            zone_a.zone_type is not ZoneType.CONNECTION):

        paused_drones = [
            d for d in drones_in_zone
            if position_this_turn(rend, d) is not
            position_next_turn(rend, d)
        ]

        for pd in paused_drones:
            pd.drones_in_zones = len(paused_drones)

        if len(paused_drones) == 1:
            return (zone_a_pos[0], zone_a_pos[1])

        return calculate_orbit(
            rend=rend,
            drone=drone,
            drone_list=paused_drones,
            center_x=zone_a_pos[0],
            center_y=zone_a_pos[1],
            mult=0.6,
        )

    moving_drones = [
        d for d in drones_in_zone
        if position_next_turn(rend, d) is
        position_next_turn(rend, drone)
    ]

    for md in moving_drones:
        md.drones_in_zones = len(moving_drones)

    center_x = int(zone_a_pos[0] + (zone_b_pos[0] - zone_a_pos[0]) * dt)
    center_y = int(zone_a_pos[1] + (zone_b_pos[1] - zone_a_pos[1]) * dt)

    if len(moving_drones) == 1:
        return (center_x, center_y)

    return calculate_orbit(
        rend=rend,
        drone=drone,
        drone_list=moving_drones,
        center_x=center_x,
        center_y=center_y,
        mult=0.3
    )


def calculate_orbit(
        rend: Renderer,
        drone: Drone,
        drone_list: list[Drone],
        center_x: int,
        center_y: int,
        mult: float,
        waiting: bool = False,
        single: bool = False
        ) -> tuple[int, int]:
    """Compute a drone position on an orbital layout.

    Args:
        drone (Drone): drone being positioned.
        drone_list (list[Drone]): other drones sharing the same space.
        center_x (int): center X coordinate.
        center_y (int): center Y coordinate.
        mult (float): orbit multiplier.
        waiting (bool): when True, use waiting orbit logic.
        single (bool): when True, use single orbit logic.

    Returns:
        tuple[int, int]: screen coordinates for the drone.
    """
    i = drone_list.index(drone)
    angle = (
        rend.drone_angles[drone.drone_id]
        + ((2 * math.pi / len(drone_list)) * i)
    )

    orbit_r = ZONE_R * mult
    if waiting is True:
        if single is False:
            orbit_r += rend.orbit_offset

        # waiting drones rotate counter clockwise
        x = center_x - int(orbit_r * math.cos(angle))

    else:
        x = center_x + int(orbit_r * math.cos(angle))

    y = center_y + int(orbit_r * math.sin(angle))
    return (x, y)


def position_this_turn(
        rend: Renderer,
        drone: Drone
        ) -> Zone | None:
    """Return the zone of a drone at the current turn.

    Args:
        drone (Drone): drone to query.

    Returns:
        Zone | None: current zone of the drone.
    """
    return drone.position_at_turn(int(rend.current_turn))


def position_next_turn(
        rend: Renderer,
        drone: Drone
        ) -> Zone | None:
    """Return the zone of a drone on the next turn.

    Args:
        drone (Drone): drone to query.

    Returns:
        Zone | None: next zone of the drone.
    """
    return drone.position_at_turn(int(rend.current_turn) + 1)


def later_next_turn(
        rend: Renderer,
        drone: Drone
        ) -> Zone | None:
    """Return the zone of a drone at the turn after the next.

    Args:
        drone (Drone): drone to query.

    Returns:
        Zone | None: zone after the next turn.
    """
    return drone.position_at_turn(
            math.ceil(rend.current_turn + 1)
        )
