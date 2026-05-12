"""Hover detection and highlight rendering helpers."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rendering.renderer import Renderer
    from src.types import Path

from src.connection import Connection
from src.zone import Zone
from src.drone import Drone

from rendering.data import TEXT_COLOR, ZONE_R, SCREEN_COLOR, DRONE_R, CONN_W
from rendering.utils.tools import (get_random_color,
                                   build_connection_path)

import rendering.utils.mousehover as hover
import rendering.utils.positions as getpos
import rendering.draw.build_tooltips as tooltip
import rendering.draw.draw_templates as draw
import pygame


def draw_hovered(rend: Renderer) -> None:
    """Render hover effects for hovered simulation entities."""
    if rend.current_turn >= rend.max_turn:
        return

    hovered: tuple[list[Drone], list[Zone], list[Connection]] = (
        hover.h_drones(rend, DRONE_R),
        hover.h_zones(rend, ZONE_R),
        hover.h_connections(rend, 6.9)
    )
    color = get_random_color() if rend.random_color else TEXT_COLOR

    if rend.path_view:
        return hovered_paths(rend, hovered, color)

    if len(hovered[0]) > 0:
        return hovered_drones(rend, hovered[0], color)

    if len(hovered[1]) > 0:
        return hovered_zones(rend, hovered[1], color)

    if len(hovered[2]) > 0:
        return hovered_connections(rend, hovered[2], color)


def hovered_drones(
        rend: Renderer,
        lst: list[Drone],
        color: tuple[int, int, int]
        ) -> None:
    """Draw hover tooltips for hovered drones."""
    offset: int = 0
    for drone in lst:

        pos = getpos.get_drone_position(rend, drone)
        if pos is None:
            continue

        d_lines = tooltip.drone(drone, rend)
        draw.draw_drone(rend.screen, pos, color, hovered=True)
        draw.draw_tooltip(rend.screen, color, rend.tooltip_font, d_lines,
                          pos=(30, 30 + offset))
        offset += rend.tooltip_font.get_linesize() * len(d_lines) + 30


def hovered_connections(
        rend: Renderer,
        lst: list[Connection],
        color: tuple[int, int, int]
        ) -> None:
    """Draw hover tooltips for hovered connections."""
    offset: int = 0
    for connection in lst:

        pos = rend.c_positions.get(connection)
        if pos is None:
            continue

        start = rend.z_positions.get(connection.zone_a)
        end = rend.z_positions.get(connection.zone_b)
        if start is None or end is None:
            continue

        c_lines = tooltip.connection(connection)
        draw.draw_connection(rend.screen, start, end, color, hovered=True)
        draw.draw_tooltip(rend.screen, color,
                          rend.tooltip_font, c_lines,
                          pos=(30, 30 + offset))
        offset += rend.tooltip_font.get_linesize() * len(c_lines) + 30


def hovered_zones(
        rend: Renderer,
        lst: list[Zone],
        color: tuple[int, int, int]
        ) -> None:
    """Draw hover tooltips for hovered zones and their neighbors."""
    offset: int = 0
    for zone in lst:
        start = rend.z_positions.get(zone)
        if start is None:
            continue

        z_lines = tooltip.zone(zone, rend)
        neighbors = rend.graph.get_neighbors(
            zone, rend.graph.render_grid.connections
            )

        if len(neighbors) == 0:
            draw.draw_zone(rend.screen, start, color, hovered=True)
        else:
            z_lines.extend(["", "NEIGHBORS:"])

        for z in neighbors:
            end = rend.z_positions.get(z)
            if end is None:
                continue
            draw.draw_connection(rend.screen, start, end, color, hovered=True)
            z_lines.extend(tooltip.neighbor(z))

        draw.draw_tooltip(rend.screen, color,
                          rend.tooltip_font, z_lines,
                          pos=(30, 30 + offset))
        offset += rend.tooltip_font.get_linesize() * len(z_lines) + 30


def hovered_paths(
        rend: Renderer,
        hovered: tuple[list[Drone], list[Zone], list[Connection]],
        color: tuple[int, int, int]
        ) -> None:
    """Draw hover overlays for paths while path view is active."""
    offset: int = 0
    h_offset: int = 0
    max_w: int = 0
    chosen_p: Path | None = None
    path_ids: set[int] = set()

    if len(hovered[0]) > 0:
        for drone in hovered[0]:
            pos = getpos.get_drone_position(rend, drone)
            if pos is None:
                continue
            draw.draw_drone(rend.screen, pos, color, hovered=True)
            zone_list = [i[1] for i in drone.path if not i[1].is_start]
            zone_list.insert(0, drone.path[0][1])
            conn_list = build_connection_path(zone_list)

            for c in conn_list:
                start = rend.z_positions.get(c.zone_a)
                end = rend.z_positions.get(c.zone_b)
                if start is None or end is None:
                    continue
                draw.draw_connection(rend.screen, start, end, color, True)

            for p in rend.paths:
                if p['c_path'] == conn_list:
                    chosen_p = p
                    break
            if not chosen_p or chosen_p['path_id'] in path_ids:
                continue
            path_ids.add(chosen_p['path_id'])

            p_lines = tooltip.path(chosen_p, rend)
            curr_w = max(rend.tooltip_font.size(s)[0] for s in p_lines)
            if max_w < curr_w:
                max_w = curr_w

            draw.draw_tooltip(rend.screen, color,
                              rend.tooltip_font, p_lines,
                              pos=(30 + h_offset, 30 + offset))

            tt_offset = rend.tooltip_font.get_linesize() * len(p_lines)
            offset += tt_offset + 30
            if offset + tt_offset > rend.screen.get_height():
                offset = 0
                h_offset += max_w + 30

    elif len(hovered[1]) > 0:
        for hz in hovered[1]:
            start = rend.z_positions.get(hz)
            if start is None:
                continue

            c_paths = [[c for c in p['c_path'] if hz in p['z_path']]
                       for p in rend.paths]

            for conn_list in c_paths:
                for c in conn_list:
                    start = rend.z_positions.get(c.zone_a)
                    end = rend.z_positions.get(c.zone_b)
                    if start is None or end is None:
                        continue
                    draw.draw_connection(rend.screen, start, end, color, True)

                for p in rend.paths:
                    if p['c_path'] == conn_list:
                        chosen_p = p
                        break
                if not chosen_p or chosen_p['path_id'] in path_ids:
                    continue
                path_ids.add(chosen_p['path_id'])

                p_lines = tooltip.path(chosen_p, rend)
                curr_w = max(rend.tooltip_font.size(s)[0] for s in p_lines)
                if max_w < curr_w:
                    max_w = curr_w

                draw.draw_tooltip(rend.screen, color,
                                  rend.tooltip_font, p_lines,
                                  pos=(30 + h_offset, 30 + offset))

                tt_offset = rend.tooltip_font.get_linesize() * len(p_lines)
                offset += tt_offset + 30
                if offset + tt_offset > rend.screen.get_height():
                    offset = 0
                    h_offset += max_w + 30

    elif len(hovered[2]) > 0:
        for hc in hovered[2]:
            pos = rend.c_positions.get(hc)
            if pos is None:
                continue

            c_paths = [[c for c in p['c_path'] if hc in p['c_path']]
                       for p in rend.paths]

            for conn_list in c_paths:
                for c in conn_list:
                    start = rend.z_positions.get(c.zone_a)
                    end = rend.z_positions.get(c.zone_b)
                    if start is None or end is None:
                        continue
                    draw.draw_connection(rend.screen, start, end, color, True)

                for p in rend.paths:
                    if p['c_path'] == conn_list:
                        chosen_p = p
                        break
                if not chosen_p or chosen_p['path_id'] in path_ids:
                    continue
                path_ids.add(chosen_p['path_id'])

                p_lines = tooltip.path(chosen_p, rend)
                curr_w = max(rend.tooltip_font.size(s)[0] for s in p_lines)
                if max_w < curr_w:
                    max_w = curr_w

                draw.draw_tooltip(rend.screen, color,
                                  rend.tooltip_font, p_lines,
                                  pos=(30 + h_offset, 30 + offset))

                tt_offset = rend.tooltip_font.get_linesize() * len(p_lines)
                offset += tt_offset + 30
                if offset + tt_offset > rend.screen.get_height():
                    offset = 0
                    h_offset += max_w + 30


def draw_info(rend: Renderer) -> None:
    """Render the HUD info panel for the current renderer state."""
    width, _ = rend.hud_font_bold.size("DATA")
    screen_w = rend.screen.get_width()
    color = get_random_color() if rend.random_color else TEXT_COLOR

    rend.buttons['info'] = draw.draw_button(
        rend.screen, color, rend.title_font, ["IN", "FO"],
        (screen_w, 0), interline=-18, offset=(-(width + 30), 30),
        frame=True
    )

    hbs = hover.h_buttons(rend)
    if hbs is None:
        return

    info_label = ""
    for s in hbs:
        if s == "info":
            info_label = s
            break
    if info_label == "":
        return

    frame = rend.buttons['info']
    frame_cx, frame_cy = frame.center

    pygame.draw.rect(rend.screen, SCREEN_COLOR, frame)
    kd = ['keys', 'data']
    pygame.draw.rect(
        rend.screen, color, frame, CONN_W,
        border_top_left_radius=-1 if any(w in hbs for w in kd) else 10,
        border_top_right_radius=10,
        border_bottom_left_radius=-1 if any(w in hbs for w in kd) else 10,
        border_bottom_right_radius=10
        )

    rend.buttons['keys'] = draw.draw_label(
        rend.screen, "KEYS", (frame_cx, frame_cy),
        rend.hud_font_bold, TEXT_COLOR,
        offset=(0, -22), is_info=True
    )
    rend.buttons['data'] = draw.draw_label(
        rend.screen, "DATA", (frame_cx, frame_cy),
        rend.hud_font_bold, TEXT_COLOR,
        offset=(0, 21), is_info=True
    )
    pygame.draw.line(rend.screen, color,
                     (frame_cx - width // 2, frame_cy),
                     (frame_cx + width // 2, frame_cy), 1)

    for hb in hbs:
        lines = []
        if hb == "keys":
            lines.extend(tooltip.keys())
            draw.draw_tooltip(rend.screen, color, rend.tooltip_font,
                              lines, (frame.left + 2, frame.top),
                              is_info=True)

        elif hb == "data":
            lines.extend(tooltip.data(rend))
            draw.draw_tooltip(rend.screen, color, rend.tooltip_font,
                              lines, (frame.left + 2, frame.top),
                              is_info=True)
