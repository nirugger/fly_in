"""Renderer draw routines for the Fly In simulation."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rendering.renderer import Renderer

from rendering.draw.draw_hovered import draw_hovered, draw_info
from rendering.utils.positions import get_drone_position
from rendering.utils.tools import get_random_color, get_zone_color

from rendering.data import TEXT_COLOR, DRONE_COLOR, CONN_W
from src.zone import ZoneType

import rendering.draw.draw_templates as draw
import pygame


def drones(rend: Renderer) -> None:
    """Draw all drones in the current simulation state."""
    for drone in rend.drones:
        pos = get_drone_position(rend, drone)
        if pos is None:
            continue

        color = (
            get_random_color()
            if rend.random_color
            else DRONE_COLOR
        )
        draw.draw_drone(rend.screen, pos, color)


def zones(rend: Renderer) -> None:
    """Draw all non-connection zones in the renderer."""
    for zone, position in rend.z_positions.items():
        if zone.zone_type is ZoneType.CONNECTION:
            continue
        color = get_zone_color(zone)
        draw.draw_zone(rend.screen, position, color)


def connections(rend: Renderer) -> None:
    """Draw the graph connections between zones."""
    for connection in rend.graph.render_grid.connections:

        start = rend.z_positions.get(connection.zone_a)
        end = rend.z_positions.get(connection.zone_b)
        if start is None or end is None:
            continue
        draw.draw_connection(rend.screen, start, end)


def hovered(rend: Renderer) -> None:
    """Render tooltip highlights for hovered objects."""
    draw_hovered(rend)


def info(rend: Renderer) -> None:
    """Render the info panel overlay when requested."""
    draw_info(rend)


def finish(
        screen: pygame.Surface,
        font: pygame.font.Font,
        color_flag: bool = False
        ) -> None:
    """Draw the simulation completion overlay."""
    color = (
        get_random_color()
        if color_flag
        else TEXT_COLOR
    )
    cx, cy = (screen.get_width() // 2,
              screen.get_height() // 2)

    overlay = pygame.Surface(
        (screen.get_width(), screen.get_height()),
        pygame.SRCALPHA
    )

    pygame.draw.rect(
        overlay,
        (0, 0, 0, 180),
        overlay.get_rect()
    )

    screen.blit(overlay, (0, 0))

    frame = draw.draw_label(screen, "SIMULATION COMPLETE", (cx, cy),
                            font, color)

    pygame.draw.line(
        screen, color, frame.bottomleft, frame.bottomright, CONN_W
    )
