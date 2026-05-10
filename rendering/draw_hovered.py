from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rendering.renderer import Renderer

from src.connection import Connection
from src.zone import Zone
from src.drone import Drone

from rendering.data import TEXT_COLOR, ZONE_R, SCREEN_COLOR, DRONE_R, CONN_W
from rendering.utils import (get_random_color,
                             build_connection_path,
                             get_neighbors)
from rendering.templates import (draw_drone,
                                 draw_zone,
                                 draw_connection,
                                 draw_label,
                                 draw_button,
                                 draw_tooltip,)

import pygame
import rendering.mousehover as mh
import rendering.positions as getpos
import rendering.build_tooltips as bt


def draw_hovered(rend: Renderer) -> None:

    if rend.current_turn >= rend.max_turn:
        return

    hovered: tuple[list[Drone], list[Zone], list[Connection]] = (
        mh.h_drones(rend, DRONE_R),
        mh.h_zones(rend, ZONE_R),
        mh.h_connections(rend, 6.9)
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
    offset: int = 0
    for drone in lst:

        pos = getpos.get_drone_position(rend, drone)
        if pos is None:
            continue

        d_lines = bt.drone(drone, rend)
        draw_drone(rend.screen, pos, color, hovered=True)
        draw_tooltip(rend.screen, color, rend.tooltip_font, d_lines,
                     pos=(30, 30 + offset))
        offset += rend.tooltip_font.get_linesize() * len(d_lines) + 30


def hovered_connections(
        rend: Renderer,
        lst: list[Connection],
        color: tuple[int, int, int]
        ) -> None:

    offset: int = 0
    for connection in lst:

        pos = rend.c_positions.get(connection)
        if pos is None:
            continue

        start = rend.z_positions.get(connection.zone_a)
        end = rend.z_positions.get(connection.zone_b)
        if start is None or end is None:
            continue

        c_lines = bt.connection(connection)
        draw_connection(rend.screen, start, end, color, hovered=True)
        draw_tooltip(rend.screen, color,
                     rend.tooltip_font, c_lines,
                     pos=(30, 30 + offset))
        offset += rend.tooltip_font.get_linesize() * len(c_lines) + 30


def hovered_zones(
        rend: Renderer,
        lst: list[Zone],
        color: tuple[int, int, int]
        ) -> None:
    offset: int = 0
    for zone in lst:
        start = rend.z_positions.get(zone)
        if start is None:
            continue

        z_lines = bt.zone(zone, rend)
        neighbors = get_neighbors(zone,
                                  rend.graph.render_grid.connections)

        if len(neighbors) == 0:
            draw_zone(rend.screen, start, color, hovered=True)
        else:
            z_lines.extend(["", "NEIGHBORS:"])

        for z in neighbors:
            end = rend.z_positions.get(z)
            if end is None:
                continue
            draw_connection(rend.screen, start, end, color, hovered=True)
            z_lines.extend(bt.neighbor(z))

        draw_tooltip(rend.screen, color,
                     rend.tooltip_font, z_lines,
                     pos=(30, 30 + offset))
        offset += rend.tooltip_font.get_linesize() * len(z_lines) + 30

# def pathtips(
#         rend: Renderer,
#         hovered_cs: list[Connection],
#         hovered_zs: list[Zone],
#         hovered_ds: list[Drone],
#         color: tuple[int, int, int]
#         ) -> None:

#     # path = {}
#     if (len(hovered_ds) > 0
#             and rend.current_turn < rend.max_turn):
#         offset: int = 0
#         for drone in hovered_ds:
#             pos = rend._get_drone_position(drone)
#             if pos is None:
#                 continue

#             draw_drone(rend.screen, pos, color, hovered=True)
#             zone_list = [i[1] for i in drone.path if not i[1].is_start]
#             zone_list.insert(0, drone.path[0][1])
#             # conn_list = build_connection_path(zone_list)
#             for p in rend.paths:
#                 if p['z_path'] == zone_list:
#                     chosen_p = p
#                     break

#             p_lines = [
#                 f"TOTAL COST : {chosen_p['cost']}"
#                 # f"{sum(z.movement_cost for z in zone_list)} turns",
#                 f"CAPACITY : {chosen_p['cap']}",
#                 # f"CHOSEN BY : {going if going != being else 'wait'}"
#             ]

#             draw_tooltip(rend.screen, color,
#                             rend.tooltip_font, p_lines,
#                             pos=(30, 30 + offset))
#             offset += rend.tooltip_font.get_linesize() * len(p_lines) + 30


def hovered_paths(
        rend: Renderer,
        hovered: tuple[list[Drone], list[Zone], list[Connection]],
        color: tuple[int, int, int]
        ) -> None:

    if len(hovered[0]) > 0:
        for drone in hovered[0]:
            pos = getpos.get_drone_position(rend, drone)
            if pos is None:
                continue
            draw_drone(rend.screen, pos, color, hovered=True)
            zone_list = [i[1] for i in drone.path if not i[1].is_start]
            zone_list.insert(0, drone.path[0][1])
            conn_list = build_connection_path(zone_list)

            for c in conn_list:
                start = rend.z_positions.get(c.zone_a)
                end = rend.z_positions.get(c.zone_b)
                if start is None or end is None:
                    continue
                draw_connection(rend.screen, start, end, color, hovered=True)

    elif len(hovered[1]) > 0:
        for hz in hovered[1]:
            start = rend.z_positions.get(hz)
            if start is None:
                continue

            c_paths = [[c for c in p['c_path'] if hz in p['z_path']]
                       for p in rend.paths]

            for lst in c_paths:
                for c in lst:
                    start = rend.z_positions.get(c.zone_a)
                    end = rend.z_positions.get(c.zone_b)
                    if start is None or end is None:
                        continue
                    draw_connection(rend.screen, start, end, color, True)

    elif len(hovered[2]) > 0:
        for hc in hovered[2]:
            pos = rend.c_positions.get(hc)
            if pos is None:
                continue

            c_paths = [[c for c in p['c_path'] if hc in p['c_path']]
                       for p in rend.paths]

            for lst in c_paths:
                for c in lst:
                    start = rend.z_positions.get(c.zone_a)
                    end = rend.z_positions.get(c.zone_b)
                    if start is None or end is None:
                        continue
                    draw_connection(rend.screen, start, end, color, True)


def draw_info(rend: Renderer) -> None:

    width, _ = rend.hud_font_bold.size("DATA")
    screen_w = rend.screen.get_width()
    color = get_random_color() if rend.random_color else TEXT_COLOR

    rend.buttons['info'] = draw_button(
        rend.screen, color, rend.title_font, ["IN", "FO"],
        (screen_w, 0), interline=-18, offset=(-(width + 30), 30),
        frame=True
    )

    hbs = mh.h_buttons(rend)
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

    rend.buttons['keys'] = draw_label(
        rend.screen, "KEYS", (frame_cx, frame_cy),
        rend.hud_font_bold, TEXT_COLOR,
        offset=(0, -22), is_info=True
    )
    rend.buttons['data'] = draw_label(
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
            lines.extend(bt.keys())
            draw_tooltip(rend.screen, color,
                         rend.tooltip_font, lines,
                         (frame.left + 2, frame.top), is_info=True)

        elif hb == "data":
            lines.extend(bt.data(rend))
            draw_tooltip(rend.screen, color,
                         rend.tooltip_font, lines,
                         (frame.left + 2, frame.top), is_info=True)
