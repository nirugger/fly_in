"""Rendering engine for the Fly In simulation.

This module provides rendering, input handling, and UI overlays for the
simulation scene.
"""

from src.connection import Connection
from src.zone import Zone, ZoneType
from src.drone import Drone
from src.graph import Graph
from src.types import Path

from rendering.utils import (
    average_turn_per_drone, compute_percentage, get_zone_color,
    get_random_color, get_neighbors, get_occupancy_at_turn, total_turn_cost,
    build_connection_path)

from rendering.draw import (
    draw_connection, draw_tooltip, draw_label, draw_button, draw_finish)

from rendering.data import (
    DRONE_R, ZONE_R, ZONE_R2, ZONE_W, CONN_W, SPAN,
    SCREEN_COLOR, TEXT_COLOR, DRONE_COLOR, FONT_REGULAR, FONT_BOLD)

import pygame
import math
import sys


class Renderer:
    """Display simulation state and manage playback controls."""

    def __init__(
            self,
            screen: pygame.Surface,
            graph: Graph,
            paths: list[Path]
            ) -> None:
        """Initialize the renderer with the game screen and graph.

        Args:
            screen (pygame.Surface): display surface.
            graph (Graph): simulation graph containing zones and drones.
        """
        self.screen = screen
        self.graph = graph
        self.drones = self.graph.drones
        self.paths: dict[tuple[Zone], list[Connection]] = {
            tuple(p['path']): build_connection_path(p['path']) for p in paths
        }

        self.speed: float = 0.5
        self.paused: bool = True
        self.last_int_turn: int = -1
        self.current_turn: float = 0.0
        self.max_turn = max(
            turn for drone in self.drones
            for turn, _ in drone.path
        )

        self.buttons: dict[str, pygame.Rect] = {}
        self.z_positions, self.c_positions = self._compute_layout()

        self.drones_action_map: dict[str, list[Drone]] = {}
        self.orbit_offset: float = 0.0
        self.orbit_maxxed: bool = False
        self.drone_angles: dict[int, float] = {
            drone.drone_id: 0.00 for drone in self.drones
        }

        self.total_path_cost: int = sum(d.path_cost for d in self.drones)
        self.total_simulation_cost: int = 0
        self.average_turn_per_drone: int = 0

        self.title_font = pygame.font.Font(FONT_BOLD, 42)
        self.tooltip_font = pygame.font.Font(FONT_REGULAR, 15)
        self.hud_font_bold = pygame.font.Font(FONT_REGULAR, 20)

        self.path_view: bool = False
        self.back_to_menu: bool = False
        self.random_color: bool = False

    def _compute_layout(self) -> tuple[
        dict[Zone, tuple[int, int]], dict[Connection, tuple[int, int]]
    ]:
        """Compute screen positions for every zone.

        Returns:
            tuple[
                dict[Zone, tuple[int, int]]: mapping from zones to pixel
                    coordinates,
                dict[Connection, tuple[int, int]]: mapping from connections
                    to pixel coordinates.
            ]
        """
        zones = self.graph.render_grid.zones
        xs = [zone.x for zone in zones]
        ys = [zone.y for zone in zones]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        span_x = max(max_x - min_x, 1)
        span_y = max(max_y - min_y, 1)

        margin = 100
        width = self.screen.get_width()
        height = self.screen.get_height()

        raw_positions: dict[Zone, tuple[int, int]] = {}
        for zone in zones:
            if zone.zone_type is not ZoneType.CONNECTION:
                nx = (zone.x - min_x) / span_x
                ny = 1.0 - (zone.y - min_y) / span_y
                px = int(margin + nx * (width - 2 * margin))
                py = int(margin + ny * (height - 2 * margin))
                raw_positions[zone] = (px, py)

        all_ys = [pos[1] for pos in raw_positions.values()]
        all_xs = [pos[0] for pos in raw_positions.values()]
        content_cy = (min(all_ys) + max(all_ys)) // 2
        content_cx = (min(all_xs) + max(all_xs)) // 2
        screen_cy = height // 2
        screen_cx = width // 2

        dy = screen_cy - content_cy
        dx = screen_cx - content_cx

        z_positions: dict[Zone, tuple[int, int]] = {}
        c_positions: dict[Connection, tuple[int, int]] = {}

        for zone in zones:
            if zone.zone_type is not ZoneType.CONNECTION:
                px, py = raw_positions[zone]
                z_positions[zone] = (px + dx, py + dy)

        for conn in self.graph.render_grid.connections:
            pos_a = z_positions.get(conn.zone_a)
            pos_b = z_positions.get(conn.zone_b)
            if pos_a is None or pos_b is None:
                continue

            middleground = (
                    (pos_a[0] + pos_b[0]) // 2,
                    (pos_a[1] + pos_b[1]) // 2
                )

            if conn.zone_c is not None:
                z_positions[conn.zone_c] = middleground
            c_positions[conn] = middleground

        return (z_positions, c_positions)

    def run(self) -> None:
        """Start the renderer main loop.

        The loop handles event processing, updates, and drawing until the
        user returns to the menu or quits the program.
        """
        clock = pygame.time.Clock()

        while True:
            dt = clock.tick(60) / 1000.0
            self._handle_events()
            self._handle_turns(dt)

            self._update_drones_action_map()
            self._update_angles_and_orbit(dt)

            self._draw_frame()
            pygame.display.flip()

            if self.back_to_menu:
                return self.random_color

    # --- RENDERING ----------------------------------------------------------

    def _draw_frame(self) -> None:
        """Render the current simulation frame."""
        self.screen.fill(SCREEN_COLOR)
        self._draw_connections()
        self._draw_zones()
        self._draw_hovered()
        self._draw_drones()
        self._draw_tooltips()
        if self.current_turn >= self.max_turn:
            draw_finish(self.screen, self.title_font, self.random_color)
        self._draw_info()

    def _draw_connections(self) -> None:
        for connection in self.graph.render_grid.connections:

            start = self.z_positions.get(connection.zone_a)
            end = self.z_positions.get(connection.zone_b)
            if start is None or end is None:
                continue
            draw_connection(self.screen, start, end)

    def _draw_zones(self) -> None:
        for zone, position in self.z_positions.items():
            if zone.zone_type is ZoneType.CONNECTION:
                continue

            color = get_zone_color(zone)
            pygame.draw.circle(self.screen, SCREEN_COLOR, position, ZONE_R2)
            pygame.draw.circle(self.screen, color, position, ZONE_R, ZONE_W)

    def _draw_hovered(self) -> None:

        hovered_zs: list[Zone] = self._hovered_zone(ZONE_R)
        hovered_ds: list[Drone] = self._hovered_drones(DRONE_R)
        hovered_cs: list[Connection] = self._hovered_connection(10.0)
        special_color = get_random_color() if self.random_color else TEXT_COLOR

        if (len(hovered_ds) > 0):
            for hd in hovered_ds:
                pos = self._get_drone_position(hd)
                if pos is None:
                    continue
                pygame.draw.circle(self.screen, special_color, pos,
                                   DRONE_R + 1, 1)
            return self._draw_path(hovered_cs, hovered_zs, special_color)

        if self.path_view:
            return self._draw_path(hovered_cs, hovered_zs, special_color)

        if (len(hovered_cs) > 0
                and len(hovered_zs) == 0
                and len(hovered_ds) == 0
                and self.current_turn < self.max_turn):

            for hc in hovered_cs:
                pos = self.c_positions.get(hc)
                if pos is None:
                    continue

                start = self.z_positions.get(hc.zone_a)
                end = self.z_positions.get(hc.zone_b)
                if start is None or end is None:
                    continue

                pygame.draw.circle(self.screen, special_color,
                                   start, ZONE_R + 2, CONN_W)
                pygame.draw.circle(self.screen, special_color,
                                   end, ZONE_R + 2, CONN_W)

                draw_connection(self.screen, start, end,
                                CONN_W, special_color)

        if (len(hovered_zs) > 0
                and len(hovered_ds) == 0
                and self.current_turn < self.max_turn):

            for hz in hovered_zs:
                start = self.z_positions.get(hz)
                if start is None:
                    continue

                neighbors = get_neighbors(hz,
                                          self.graph.render_grid.connections)
                for z in neighbors:
                    end = self.z_positions.get(z)
                    if end is None:
                        continue

                    draw_connection(self.screen, start, end,
                                    CONN_W, special_color)

                    z_color = special_color
                    # from rendering.data import COLORS
                    # match z.zone_type:
                    #     case ZoneType.NORMAL:
                    #         z_color = COLORS['highlight_normal']
                    #     case ZoneType.BLOCKED:
                    #         z_color = COLORS['highlight_blocked']
                    #     case ZoneType.RESTRICTED:
                    #         z_color = COLORS['highlight_restricted']
                    #     case ZoneType.PRIORITY:
                    #         z_color = COLORS['highlight_priority']

                    pygame.draw.circle(self.screen, z_color,
                                       end, ZONE_R + 2, CONN_W)

                pygame.draw.circle(self.screen, special_color,
                                   start, ZONE_R + 2, CONN_W)

    def _draw_path(
            self,
            hovered_cs: list[Connection],
            hovered_zs: list[Zone],
            special_color: tuple[int, int, int]
            ) -> None:

        path = {}
        if (len(hovered_cs) > 0
                and len(hovered_zs) == 0
                and self.current_turn < self.max_turn):

            for hc in hovered_cs:
                pos = self.c_positions.get(hc)
                if pos is None:
                    continue

                path = {k: v for k, v in self.paths.items() if hc in v}
                if len(path) == 0:
                    continue

                for _, v in path.items():
                    for c in v:
                        start = self.z_positions.get(c.zone_a)
                        end = self.z_positions.get(c.zone_b)
                        if start is None or end is None:
                            continue
                        pygame.draw.circle(self.screen, special_color,
                                           start, ZONE_R + 2, CONN_W)
                        pygame.draw.circle(self.screen, special_color,
                                           end, ZONE_R + 2, CONN_W)
                        draw_connection(self.screen, start, end,
                                        CONN_W, special_color)

        elif (len(hovered_zs) > 0
                and self.current_turn < self.max_turn):

            for hz in hovered_zs:
                start = self.z_positions.get(hz)
                if start is None:
                    continue

                path = {k: v for k, v in self.paths.items() if hz in k}
                if len(path) == 0:
                    continue

                for _, v in path.items():
                    for c in v:
                        start = self.z_positions.get(c.zone_a)
                        end = self.z_positions.get(c.zone_b)
                        if start is None or end is None:
                            continue
                        pygame.draw.circle(self.screen, special_color,
                                           start, ZONE_R + 2, CONN_W)
                        pygame.draw.circle(self.screen, special_color,
                                           end, ZONE_R + 2, CONN_W)
                        draw_connection(self.screen, start, end,
                                        CONN_W, special_color)

    def _draw_drones(self) -> None:
        for drone in self.drones:
            pos = self._get_drone_position(drone)
            if pos is None:
                continue

            color = (
                get_random_color()
                if self.random_color
                else DRONE_COLOR
            )

            pygame.draw.circle(self.screen, color, pos, DRONE_R)

    def _draw_tooltips(self) -> None:

        hovered_cs: list[Connection] = self._hovered_connection(10.0)
        hovered_zs: list[Zone] = self._hovered_zone(ZONE_R)
        special_color = get_random_color() if self.random_color else TEXT_COLOR

        if self.path_view is True:
            return self._draw_pathtips(hovered_cs, hovered_zs, special_color)

        if (len(hovered_cs) > 0
                and len(hovered_zs) == 0
                and self.current_turn < self.max_turn):
            offset: int = 0

            for hc in hovered_cs:
                c_lines = [
                    f"NAME : {hc.name}",
                    f"ROOM : {hc.max_link_capacity}",
                ]

                draw_tooltip(self.screen, special_color,
                             self.tooltip_font, c_lines,
                             pos=(30, 30 + offset))
                offset += self.tooltip_font.get_linesize() * len(c_lines) + 30

        if len(hovered_zs) > 0 and self.current_turn < self.max_turn:
            offset: int = 0
            for hz in hovered_zs:

                start = self.z_positions.get(hz)
                if start is None:
                    continue

                live = ""
                if self.paused and self.current_turn.is_integer():
                    counter = 0
                    for d in self.drones:
                        if d.position_at_turn(int(self.current_turn)) is hz:
                            counter += 1
                    live = f"{counter} / "

                s = "s" if hz.max_drones > 1 else ""
                z_lines: list[str] = [
                    f"NAME  : {hz.name}",
                    f"TYPE  : {hz.zone_type.value}",
                    f"ROOM  : {live}{hz.max_drones} drone{s}",
                    f"COLOR : {hz.color}"
                ]

                neighbors = get_neighbors(hz,
                                          self.graph.render_grid.connections)
                if len(neighbors) > 0:
                    z_lines.extend(["", "NEIGHBORS:"])

                for z in neighbors:
                    end = self.z_positions.get(z)
                    if end is None:
                        continue

                    cost = (z.movement_cost()
                            if z.zone_type is not ZoneType.BLOCKED
                            else 'X')
                    z_lines.append(f"cost {cost} → {z.name}")

                draw_tooltip(self.screen, special_color,
                             self.tooltip_font, z_lines,
                             pos=(30, 30 + offset))
                offset += self.tooltip_font.get_linesize() * len(z_lines) + 30

    def _draw_pathtips(
            self,
            hovered_cs: list[Connection],
            hovered_zs: list[Zone],
            special_color: tuple[int, int, int]
            ) -> None:
        pass

    def _draw_info(self) -> None:

        width, _ = self.hud_font_bold.size("DATA")
        screen_w = self.screen.get_width()
        special_color = get_random_color() if self.random_color else TEXT_COLOR

        self.buttons['info'] = draw_button(
            self.screen, special_color, self.title_font, ["IN", "FO"],
            (screen_w, 0), interline=-18, offset=(-(width + 30), 30),
            frame=True
        )

        hbs = self._hovered_button()
        if hbs is None:
            return

        info_label = ""
        for s in hbs:
            if s == "info":
                info_label = s
                break
        if info_label == "":
            return

        frame = self.buttons['info']
        frame_cx, frame_cy = frame.center

        pygame.draw.rect(self.screen, SCREEN_COLOR, frame)
        kd = ['keys', 'data']
        pygame.draw.rect(
            self.screen, special_color, frame, CONN_W,
            border_top_left_radius=-1 if any(w in hbs for w in kd) else 10,
            border_top_right_radius=10,
            border_bottom_left_radius=-1 if any(w in hbs for w in kd) else 10,
            border_bottom_right_radius=10
            )

        self.buttons['keys'] = draw_label(
            self.screen, "KEYS", (frame_cx, frame_cy),
            self.hud_font_bold, TEXT_COLOR,
            offset=(0, -22), is_info=True
        )
        self.buttons['data'] = draw_label(
            self.screen, "DATA", (frame_cx, frame_cy),
            self.hud_font_bold, TEXT_COLOR,
            offset=(0, 21), is_info=True
        )
        pygame.draw.line(self.screen, special_color,
                         (frame_cx - width // 2, frame_cy),
                         (frame_cx + width // 2, frame_cy), 1)

        for hb in hbs:
            lines = []
            if hb == "keys":
                lines = [
                    "↑ : speed up",
                    "↓ : speed down",
                    "→ : next turn",
                    "← : prev turn",
                    "",
                    "V : path view",
                    "R : rainbow",
                    "Q : quit",
                    "",
                    "SPACE  : play / pause",
                    "ESCAPE : back to menu",
                ]

                draw_tooltip(self.screen, special_color,
                             self.tooltip_font, lines,
                             (frame.left + 2, frame.top), is_info=True)

            elif hb == "data":
                lines = [
                    f"CURRENT TURN : {int(self.current_turn)}",
                    f"MAXIMUM TURN : {self.max_turn}",
                    f"COMPLETION % : {compute_percentage(self.current_turn,
                                                         self.max_turn, 2)}",
                    "",
                    "DRONES WAITING  : "
                    f"{len(self.drones_action_map['waiting'])}",
                    "DRONES PREPPING : "
                    f"{len(self.drones_action_map['prepping'])}",
                    "DRONES MOVING   : "
                    f"{len(self.drones_action_map['moving'])}",
                    "DRONES ARRIVED  : "
                    f"{len(self.drones_action_map['arrived'])}",
                    "",
                    f"TOTAL  SIMULATION  COST : {self.total_simulation_cost}",
                    "AVERAGE TURNS PER DRONE : "
                    f"{round(self.average_turn_per_drone, 2)}"

                ]

                draw_tooltip(self.screen, special_color,
                             self.tooltip_font, lines,
                             (frame.left + 2, frame.top), is_info=True)

    # --- MOUSEHOVER ---------------------------------------------------------

    def _hovered_zone(
            self,
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
        for zone, pos in self.z_positions.items():
            if zone.zone_type is ZoneType.CONNECTION:
                continue
            rx = mouse_x - pos[0]
            ry = mouse_y - pos[1]
            if math.sqrt(rx*rx + ry*ry) < zone_radius:
                z_lst.append(zone)
        return z_lst

    def _hovered_drones(
            self,
            drone_radius: float,
            ) -> list[Drone]:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        d_list: list[Drone] = []
        for drone in self.drones:
            d_pos = self._get_drone_position(drone)
            if d_pos is None:
                continue

        # for zone, pos in self.z_positions.items():
        #     if zone.zone_type is ZoneType.CONNECTION:
        #         continue
            rx = mouse_x - d_pos[0]
            ry = mouse_y - d_pos[1]
            if math.sqrt(rx*rx + ry*ry) < drone_radius:
                d_list.append(drone)
        return d_list

    def _hovered_connection(
            self,
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

        for connection in self.graph.render_grid.connections:
            pos_a = self.z_positions.get(connection.zone_a)
            pos_b = self.z_positions.get(connection.zone_b)
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
                # return connection

        return c_lst

    def _hovered_button(self) -> list[str] | None:
        """Return the currently hovered HUD button name.

        Returns:
            str | None: hovered button id or None.
        """
        mx, my = pygame.mouse.get_pos()
        buttons: list[str] = []
        for name, button in self.buttons.items():
            if button.collidepoint(mx, my):
                buttons.append(name)
        if len(buttons) > 0:
            return buttons
        return None

    # --- DRONES POSITION MANAGEMENT -----------------------------------------

    def _update_drones_action_map(self) -> dict[str, list[Drone]]:
        """Calculate drone state counts for the current turn.

        Returns:
            dict[str, int]: counts for waiting, prepping, moving, and
                arrived drones.
        """
        waiting: list[Drone] = []
        prepping: list[Drone] = []
        moving: list[Drone] = []
        arrived: list[Drone] = []

        for d in self.drones:

            ptt = self._position_this_turn(d)
            pnt = self._position_next_turn(d)
            lnt = self._later_next_turn(d)
            pat = d.position_at_turn(int(self.current_turn))

            if self.paused and self.current_turn.is_integer():
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

        self.drones_action_map = {
            'waiting': waiting,
            'prepping': prepping,
            'moving': moving,
            'arrived': arrived
        }

    def _update_angles_and_orbit(
            self,
            dt: float
            ) -> None:

        for drone in self.drones:
            self.drone_angles[drone.drone_id] += (
                self.speed * dt * (15 / drone.drones_in_zones)
            )

        if self.orbit_maxxed is False:
            self.orbit_offset += 1
        else:
            self.orbit_offset -= 1

        if self.orbit_offset > SPAN or self.orbit_offset < 0:
            self.orbit_maxxed = not self.orbit_maxxed

    def _reset_drones_sync(
            self,
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
            self.orbit_offset = orbit_offset
            self.orbit_maxxed = o_flag

        for drone in self.drones:
            if angles is True:
                self.drone_angles[drone.drone_id] = self.speed * 0.016 * 2.5
            if zones is True:
                drone.drones_in_zones = 1

    def _get_drone_position(
            self,
            drone: Drone
            ) -> tuple[int, int] | None:
        """Compute the current screen position of a drone.

        Args:
            drone (Drone): drone to position.

        Returns:
            tuple[int, int] | None: screen coordinates or None if unavailable.
        """
        zone_a = self._position_this_turn(drone)
        zone_b = self._position_next_turn(drone)
        t = int(self.current_turn)
        dt = self.current_turn - t

        if zone_a is None or zone_b is None:
            return None

        zone_a_pos = self.z_positions.get(zone_a)
        zone_b_pos = self.z_positions.get(zone_b)

        if zone_a_pos is None or zone_b_pos is None:
            return None

        drones_in_zone = get_occupancy_at_turn(t, zone_a, self.drones)

        if zone_a is zone_b:

            if self._later_next_turn(drone) is zone_a:
                waiting_drones = [
                    d for d in drones_in_zone
                    if self._position_next_turn(d) is zone_a
                    and self._later_next_turn(d) is zone_a
                ]

                for wd in waiting_drones:
                    wd.drones_in_zones = len(waiting_drones)

                return self._calculate_orbit(
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
                    if self._position_next_turn(d) is zone_a
                    and self._later_next_turn(d) is not zone_a
                ]

                for pd in prepping_drones:
                    pd.drones_in_zones = len(prepping_drones)

                if len(prepping_drones) == 1:
                    return (zone_a_pos[0], zone_a_pos[1])
                return self._calculate_orbit(
                    drone=drone,
                    drone_list=prepping_drones,
                    center_x=zone_a_pos[0],
                    center_y=zone_a_pos[1],
                    mult=0.5,
                )

        if (float(self.current_turn).is_integer() and
                zone_a.zone_type is not ZoneType.CONNECTION):

            paused_drones = [
                d for d in drones_in_zone
                if self._position_this_turn(d) is not
                self._position_next_turn(d)
            ]

            for pd in paused_drones:
                pd.drones_in_zones = len(paused_drones)

            if len(paused_drones) == 1:
                return (zone_a_pos[0], zone_a_pos[1])

            return self._calculate_orbit(
                drone=drone,
                drone_list=paused_drones,
                center_x=zone_a_pos[0],
                center_y=zone_a_pos[1],
                mult=0.5,
            )

        moving_drones = [
            d for d in drones_in_zone
            if self._position_next_turn(d) is
            self._position_next_turn(drone)
        ]

        for md in moving_drones:
            md.drones_in_zones = len(moving_drones)

        center_x = int(zone_a_pos[0] + (zone_b_pos[0] - zone_a_pos[0]) * dt)
        center_y = int(zone_a_pos[1] + (zone_b_pos[1] - zone_a_pos[1]) * dt)

        if len(moving_drones) == 1:
            return (center_x, center_y)

        return self._calculate_orbit(
            drone=drone,
            drone_list=moving_drones,
            center_x=center_x,
            center_y=center_y,
            mult=0.3
        )

    def _calculate_orbit(
            self,
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
            self.drone_angles[drone.drone_id]
            + ((2 * math.pi / len(drone_list)) * i)
        )

        orbit_r = ZONE_R * mult
        if waiting is True:
            if single is False:
                orbit_r += self.orbit_offset

            # waiting drones rotate counter clockwise
            x = center_x - int(orbit_r * math.cos(angle))

        else:
            x = center_x + int(orbit_r * math.cos(angle))

        y = center_y + int(orbit_r * math.sin(angle))
        return (x, y)

    def _position_this_turn(
            self,
            drone: Drone
            ) -> Zone | None:
        """Return the zone of a drone at the current turn.

        Args:
            drone (Drone): drone to query.

        Returns:
            Zone | None: current zone of the drone.
        """
        return drone.position_at_turn(int(self.current_turn))

    def _position_next_turn(
            self,
            drone: Drone
            ) -> Zone | None:
        """Return the zone of a drone on the next turn.

        Args:
            drone (Drone): drone to query.

        Returns:
            Zone | None: next zone of the drone.
        """
        return drone.position_at_turn(int(self.current_turn) + 1)

    def _later_next_turn(
            self,
            drone: Drone
            ) -> Zone | None:
        """Return the zone of a drone at the turn after the next.

        Args:
            drone (Drone): drone to query.

        Returns:
            Zone | None: zone after the next turn.
        """
        return drone.position_at_turn(
                math.ceil(self.current_turn + 1)
            )

    # --- SIMULATION AND DATA ------------------------------------------------

    def _handle_events(self) -> None:
        """Handle keyboard and window events for the renderer."""
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused

                if event.key == pygame.K_RIGHT:
                    self._reset_drones_sync()
                    self.current_turn = min(
                        int(self.current_turn) + 1.0, float(self.max_turn)
                    ) if self.paused else min(
                        self.current_turn + 1.0, float(self.max_turn)
                    )

                if event.key == pygame.K_LEFT:
                    self._reset_drones_sync()
                    self.current_turn = max(
                        math.ceil(self.current_turn) - 1.0, 0.0
                    ) if self.paused else max(
                        self.current_turn - 1.0, 0.0
                    )

                if event.key == pygame.K_UP:
                    if self.paused and self.speed < 0:
                        self.speed = 0.25

                    else:
                        self.speed = min(42.0, self.speed + 0.25)
                    self.paused = False

                if event.key == pygame.K_DOWN:
                    if self.paused and self.speed > 0:
                        self.speed = -0.25
                    else:
                        self.speed = max(-1.0, self.speed - 0.25)
                    self.paused = False

                if event.key == pygame.K_ESCAPE:
                    self.back_to_menu = True

                if event.key == pygame.K_v:
                    self.path_view = not self.path_view

                if event.key == pygame.K_r:
                    self.random_color = not self.random_color

                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def _handle_turns(
            self,
            dt: float
            ) -> None:

        if not self.paused:
            self.current_turn += self.speed * dt

        if self.current_turn >= self.max_turn:
            self.current_turn = float(self.max_turn)
            self.paused = True

        if self.current_turn < 0.0:
            self.current_turn = 0.0
            self.last_int_turn = -1
            self.paused = True
            self.speed = 1.0

        current_int_turn = int(self.current_turn)
        if self.last_int_turn != current_int_turn:
            sign = 1 if self.last_int_turn < current_int_turn else -1
            self.last_int_turn = current_int_turn

            self.total_simulation_cost += (
                sign * total_turn_cost(self.drones, current_int_turn)
            )
            self.average_turn_per_drone = average_turn_per_drone(
                self.drones, current_int_turn)

            self._reset_drones_sync(orbit=False)
