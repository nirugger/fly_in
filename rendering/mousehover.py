from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rendering.renderer import Renderer
    from rendering.menu import Menu

from rendering.positions import get_drone_position

from src.connection import Connection
from src.zone import Zone, ZoneType
from src.drone import Drone

import pygame
import math


def h_zones(
        rend: Renderer,
        zone_radius: float
        ) -> list[Zone]:
    """Return the zone currently under the mouse cursor.

    Args:
        ZONE_R (float): radius used for hit detection.

    Returns:
        Zone | None: hovered zone or None if none is hovered.
    """
    mouse_x, mouse_y = pygame.mouse.get_pos()
    z_lst: list[Zone] = []
    for zone, pos in rend.z_positions.items():
        if zone.zone_type is ZoneType.CONNECTION:
            continue
        rx = mouse_x - pos[0]
        ry = mouse_y - pos[1]
        if math.sqrt(rx*rx + ry*ry) < zone_radius:
            z_lst.append(zone)
    return z_lst


def h_drones(
        rend: Renderer,
        drone_radius: float,
        ) -> list[Drone]:
    mouse_x, mouse_y = pygame.mouse.get_pos()
    d_list: list[Drone] = []
    for drone in rend.drones:
        d_pos = get_drone_position(rend, drone)
        if d_pos is None:
            continue

    # for zone, pos in rend.z_positions.items():
    #     if zone.zone_type is ZoneType.CONNECTION:
    #         continue
        rx = mouse_x - d_pos[0]
        ry = mouse_y - d_pos[1]
        if math.sqrt(rx*rx + ry*ry) < drone_radius:
            d_list.append(drone)
    return d_list


def h_connections(
        rend: Renderer,
        threshold: float = 8.0
        ) -> list[Connection]:
    """Return the connection currently under the mouse cursor.

    Args:
        threshold (float): max pixel distance from the line.

    Returns:
        Connection | None: hovered connection or None if none is hovered.
    """
    mx, my = pygame.mouse.get_pos()

    c_lst: list[Connection] = []

    for connection in rend.graph.render_grid.connections:
        pos_a = rend.z_positions.get(connection.zone_a)
        pos_b = rend.z_positions.get(connection.zone_b)
        if pos_a is None or pos_b is None:
            continue

        ax, ay = pos_a
        bx, by = pos_b
        # mx, my = mouse_x, mouse_y

        ab_x, ab_y = bx - ax, by - ay
        am_x, am_y = mx - ax, my - ay

        ab_len_sq = ab_x * ab_x + ab_y * ab_y
        if ab_len_sq == 0:
            continue

        t = (am_x * ab_x + am_y * ab_y) / ab_len_sq
        t = max(0.0, min(1.0, t))

        closest_x = ax + t * ab_x
        closest_y = ay + t * ab_y

        dist = math.sqrt(
            (mx - closest_x) ** 2 + (my - closest_y) ** 2
        )

        if dist < threshold:
            c_lst.append(connection)

    return c_lst


def h_buttons(rend: Renderer) -> list[str] | None:
    """Return the currently hovered HUD button name.

    Returns:
        str | None: hovered button id or None.
    """
    mx, my = pygame.mouse.get_pos()
    buttons: list[str] = []
    for name, button in rend.buttons.items():
        if button.collidepoint(mx, my):
            buttons.append(name)
    if len(buttons) > 0:
        return buttons
    return None


def h_button(menu: Menu) -> str | None:
    """Return the name of the button currently under the mouse.

    Returns:
        str | None: button key when hovered, otherwise None.
    """
    mx, my = pygame.mouse.get_pos()
    for name, button in menu.buttons.items():
        if button.collidepoint(mx, my):
            return name
    return None
