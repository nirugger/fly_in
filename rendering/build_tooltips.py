from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rendering.renderer import Renderer

from src.connection import Connection
from src.zone import Zone, ZoneType
from src.drone import Drone

import rendering.positions as getpos


def drone(drone: Drone, rend: Renderer) -> list[str]:
    current_z = ""
    next_z = ""
    for _, z in drone.path:
        if z is getpos.position_this_turn(rend, drone):
            current_z = z.name
        if z is getpos.position_next_turn(rend, drone):
            next_z = z.name

    return [
        f"DRONE ID : {drone.drone_id}",
        f"STAY IN : {current_z}",
        f"MOVE TO : {next_z if next_z != current_z else 'wait'}"
    ]


def zone(zone: Zone, rend: Renderer) -> list[str]:

    drones = ""
    if rend.paused and rend.current_turn.is_integer():
        counter = 0
        for d in rend.drones:
            if d.position_at_turn(int(rend.current_turn)) is zone:
                counter += 1
        drones = f"{counter} / "

    s = "s" if zone.max_drones > 1 else ""
    return [
        f"NAME  : {zone.name}",
        f"TYPE  : {zone.zone_type.value}",
        f"ROOM  : {drones}{zone.max_drones} drone{s}",
        f"COLOR : {zone.color}"
    ]


def neighbor(zone: Zone) -> list[str]:
    cost = (zone.movement_cost()
            if zone.zone_type is not ZoneType.BLOCKED
            else 'X')
    return [
        f"cost {cost} → {zone.name}",
    ]


def connection(connection: Connection) -> list[str]:
    return [
        f"NAME : {connection.name}",
        f"ROOM : {connection.max_link_capacity}",
    ]
