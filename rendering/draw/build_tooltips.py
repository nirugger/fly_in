from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rendering.renderer import Renderer
    from src.types import Path

from rendering.utils.tools import compute_percentage

from src.drone import Drone
from src.zone import Zone, ZoneType
from src.connection import Connection

import rendering.utils.positions as getpos


def drone(drone: Drone, rend: Renderer) -> list[str]:
    current_z = ""
    next_z = ""
    for _, z in drone.path:
        if z is getpos.position_this_turn(rend, drone):
            current_z = z.name
        if z is getpos.position_next_turn(rend, drone):
            next_z = z.name

    return [
        f"DRONE  ID : {drone.drone_id}",
        f"THIS TURN : {current_z}",
        f"NEXT TURN : {next_z}"
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


def path(p: Path, rend: Renderer) -> list[str]:

    drones_on_path: int = 0
    for d in rend.drones:
        zone_list = [i[1] for i in d.path if not i[1].is_start]
        zone_list.insert(0, d.path[0][1])
        if p["z_path"] == zone_list:
            drones_on_path += 1

    return [
        f"PATH ID    : {p['path_id']}",
        f"TOTAL COST : {p['cost']}",
        f"CAPACITY   : {p['cap']}",
        f"CHOSEN BY  : {drones_on_path} / {len(rend.drones)}"
    ]


def keys() -> list[str]:

    return [
        "↑ : speed up",
        "↓ : speed down",
        "→ : next turn",
        "← : prev turn",
        "",
        "V : path view",
        "S : stop time",
        "R : rainbow",
        "Q : quit",
        "",
        "SPACE  : play / pause",
        "ESCAPE : back to menu",
    ]


def data(rend: Renderer) -> list[str]:

    perc = compute_percentage(rend.current_turn, rend.max_turn, 2)
    return [
        f"CURRENT TURN : {int(rend.current_turn)}",
        f"MAXIMUM TURN : {rend.max_turn}",
        f"COMPLETION % : {perc}",
        "",
        "DRONES WAITING  : "
        f"{len(rend.drones_action_map['waiting'])}",
        "DRONES PREPPING : "
        f"{len(rend.drones_action_map['prepping'])}",
        "DRONES MOVING   : "
        f"{len(rend.drones_action_map['moving'])}",
        "DRONES ARRIVED  : "
        f"{len(rend.drones_action_map['arrived'])}",
        "",
        f"TOTAL  SIMULATION  COST : {rend.total_simulation_cost}",
        "AVERAGE TURNS PER DRONE : "
        f"{round(rend.average_turn_per_drone, 2)}"

    ]
