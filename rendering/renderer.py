"""Rendering engine for the Fly In simulation.

This module provides rendering, input handling, and UI overlays for the
simulation scene.
"""

from src.connection import Connection
from src.zone import Zone, ZoneType
from src.drone import Drone
from src.graph import Graph
from src.types import Path

from rendering.data import SCREEN_COLOR, FONT_REGULAR, FONT_BOLD
from rendering.utils.tools import average_turn_per_drone, total_turn_cost

import rendering.draw.draw_rend as draw
import rendering.utils.positions as pos

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
        self.paths = paths
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
        self.average_turn_per_drone: float = 0.0

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

    def run(self) -> bool:
        """Start the renderer main loop.

        The loop handles event processing, updates, and drawing until the
        user returns to the menu or quits the program.
        """
        clock = pygame.time.Clock()

        while True:
            dt = clock.tick(60) / 1000.0
            self._handle_events()
            self._handle_turns(dt)

            pos.update_drones_action_map(self)
            pos.update_angles_and_orbit(self, dt)

            self._draw_frame()
            pygame.display.flip()

            if self.back_to_menu:
                return self.random_color

    # --- RENDERING ----------------------------------------------------------

    def _draw_frame(self) -> None:
        """Render the current simulation frame."""
        self.screen.fill(SCREEN_COLOR)
        draw.connections(self)
        draw.zones(self)
        draw.drones(self)
        draw.hovered(self)
        if self.current_turn >= self.max_turn:
            draw.finish(self.screen, self.title_font, self.random_color)
        draw.info(self)

    # --- SIMULATION AND DATA ------------------------------------------------

    def _handle_events(self) -> None:
        """Handle keyboard and window events for the renderer."""
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused

                if event.key == pygame.K_RIGHT:
                    pos.reset_drones_sync(self)
                    self.current_turn = min(
                        int(self.current_turn) + 1.0, float(self.max_turn)
                    ) if self.paused else min(
                        self.current_turn + 1.0, float(self.max_turn)
                    )

                if event.key == pygame.K_LEFT:
                    pos.reset_drones_sync(self)
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

                if event.key == pygame.K_s:
                    if self.speed != 0.0:
                        self.speed = 0.0
                    else:
                        self.speed = 0.5

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

            pos.reset_drones_sync(self, orbit=False)
