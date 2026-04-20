import pygame
import sys
import math
from src.graph import Graph
from src.drone import Drone
from src.zone import Zone, ZoneType
from rendering.draw import (draw_zone,
                            draw_connection,
                            draw_label,
                            draw_hud)


class Renderer:

    def __init__(
            self,
            graph: Graph,
            drones: list[Drone]
    ) -> None:

        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.graph = graph
        self.drones = drones
        self.current_turn: float = 0.0
        self.paused: bool = False
        self.speed: float = 1.0
        self.max_turn = max(
            turn for drone in drones
            for turn, _ in drone.path
        )
        self.positions = self._compute_layout()
        self.font = pygame.font.SysFont('monospace', 16, bold=True)

        self.drone_angles: dict[int, float] = {
            drone.drone_id: 0.0 for drone in drones
        }

    def _compute_layout(
            self
    ) -> dict[Zone, tuple[int, int]]:

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

        positions: dict[Zone, tuple[int, int]] = {}
        for zone in zones:

            if zone.zone_type is ZoneType.CONNECTION:
                for conn in self.graph.render_grid.connections:
                    if conn.zone_c is zone:
                        pos_a = positions.get(conn.zone_a)
                        pos_b = positions.get(conn.zone_b)
                        if pos_a is not None and pos_b is not None:
                            positions[zone] = (
                                (pos_a[0] + pos_b[0]) // 2,
                                (pos_a[1] + pos_b[1]) // 2,
                            )
            else:
                nx = (zone.x - min_x) / span_x
                ny = 1.0 - (zone.y - min_y) / span_y
                px = int(margin + nx * (width - 2 * margin))
                py = int(margin + ny * (height - 2 * margin))
                positions[zone] = (px, py)

        return positions

    def run(
        self
    ) -> None:

        while True:
            dt = self.clock.tick(60) / 1000.0
            self._handle_events()
            if not self.paused:
                self.current_turn += self.speed * dt
            if self.current_turn >= self.max_turn:
                self.current_turn = float(self.max_turn)
                self.paused = True

            for drone in self.drones:
                self.drone_angles[drone.drone_id] += self.speed * dt * 5.0

            self._draw_frame()
            pygame.display.flip()

    def _handle_events(
            self
    ) -> None:

        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                if event.key == pygame.K_RIGHT:
                    self.current_turn = min(self.current_turn + 1.0,
                                            float(self.max_turn))
                if event.key == pygame.K_LEFT:
                    self.current_turn = max(self.current_turn - 1.0, 0.0)
                if event.key == pygame.K_UP:
                    self.speed += 0.1
                if event.key == pygame.K_DOWN:
                    self.speed = max(0.0, self.speed - 0.1)

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def _draw_frame(
            self
    ) -> None:

        self.screen.fill((15, 17, 23))
        zone_radius: float = 20
        drone_radius: float = 8
        occupancy: dict[Zone, list[Drone]] = {}
        for drone in self.drones:
            zone = drone.position_at_turn(int(self.current_turn))
            if zone is not None:
                occupancy.setdefault(zone, []).append(drone)

        draw_hud(
            surface=self.screen,
            text=f"Turn: {int(self.current_turn)}",
            position=(20, 20),
            font=self.font,
            color=(200, 200, 200)
        )

        for zone, position in self.positions.items():

            drones_in_zone = occupancy.get(zone, [])

            if zone.zone_type is ZoneType.CONNECTION:
                continue

            draw_zone(
                surface=self.screen,
                center=position,
                radius=zone_radius,
                color=(220, 80, 80) if drones_in_zone else (80, 90, 115)
            )

            draw_label(
                surface=self.screen,
                text=zone.name,
                position=(position[0], position[1] + zone_radius + 5),
                font=self.font,
                color=(80, 90, 115)
            )

            zone_type = ""
            if zone.zone_type is ZoneType.RESTRICTED:
                zone_type = "*RESTRICTED*"
            elif zone.zone_type is ZoneType.BLOCKED:
                zone_type = "*BLOCKED*"
            elif zone.zone_type is ZoneType.PRIORITY:
                zone_type = "*PRIORITY*"

            draw_label(
                surface=self.screen,
                text=zone_type,
                position=(position[0], position[1] + zone_radius + 5),
                font=self.font,
                color=(80, 90, 115),
                offset=(0, self.font.size(zone_type)[1])
            )

        for drone in self.drones:
            position = self._drone_position(drone, zone_radius)
            if position is None:
                continue
            draw_zone(
                surface=self.screen,
                center=position,
                radius=drone_radius,
                color=(220, 80, 80)
            )

        for connection in self.graph.render_grid.connections:
            start = self.positions.get(connection.zone_a)
            end = self.positions.get(connection.zone_b)
            if start is None or end is None:
                continue

            center_x = (start[0] + end[0]) // 2
            center_y = (start[1] + end[1]) // 2

            draw_connection(
                surface=self.screen,
                start=start,
                end=end,
                color=(55, 55, 55),
                width=1
            )

            draw_label(
                surface=self.screen,
                text=connection.name,
                position=(center_x, center_y),
                font=self.font,
                color=(80, 90, 115)
            )

    def _drone_position(
            self,
            drone: Drone,
            radius: float
    ) -> tuple[int, int] | None:

        zone_a = drone.position_at_turn(int(self.current_turn))
        zone_b = drone.position_at_turn(int(self.current_turn) + 1)
        t = self.current_turn - int(self.current_turn)

        if zone_a is None or zone_b is None:
            return None

        zone_a_pos = self.positions.get(zone_a)
        zone_b_pos = self.positions.get(zone_b)

        if zone_a_pos is None or zone_b_pos is None:
            return None

        if zone_a is zone_b:
            angle = self.drone_angles[drone.drone_id]
            orbit_r = radius * 2
            x = zone_a_pos[0] + int(orbit_r * math.cos(angle))
            y = zone_a_pos[1] + int(orbit_r * math.sin(angle))
            return (x, y)

        x = zone_a_pos[0] + (zone_b_pos[0] - zone_a_pos[0]) * t
        y = zone_a_pos[1] + (zone_b_pos[1] - zone_a_pos[1]) * t

        return (int(x), int(y))
