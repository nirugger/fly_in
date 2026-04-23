import pygame
import sys
import hashlib
import math
from src.graph import Graph
from src.drone import Drone
from src.zone import Zone, ZoneType
from rendering.draw import (draw_circle,
                            draw_line,
                            draw_tooltip,
                            draw_hud)

COLORS: dict[str, tuple[int, int, int]] = {
    "red": (255, 182, 185),
    "green": (182, 235, 182),
    "blue": (182, 210, 255),
    "orange": (255, 218, 182),
    "yellow": (255, 245, 182),
    "purple": (218, 182, 255),
    "cyan": (182, 245, 245),
    "pink": (255, 182, 230),
    "lime": (210, 255, 182),
    "brown": (210, 195, 175),
    "magenta": (245, 182, 235),
    "gold": (255, 235, 182),
    "violet": (200, 182, 255),
    "crimson": (255, 190, 195),
    "maroon": (220, 185, 185),
    "default": (210, 210, 215),
}


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
        self.paused: bool = True
        self.speed: float = 1.0
        self.max_turn = max(
            turn for drone in drones
            for turn, _ in drone.path
        )
        self.positions = self._compute_layout()
        self.font = pygame.font.SysFont('monospace', 14)
        self.hud_font = pygame.font.SysFont('monospace', 21, bold=True)

        self.drone_angles: dict[int, float] = {
            drone.drone_id: 0.0 for drone in drones
        }
        self.zone_radius: float = 20
        self.drone_radius: float = 5

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
                    if self.paused:
                        self.current_turn = min(
                            int(self.current_turn) + 1.0, float(self.max_turn)
                        )
                    else:
                        self.current_turn = min(
                            self.current_turn + 1.0, float(self.max_turn)
                        )

                if event.key == pygame.K_LEFT:
                    if self.paused:
                        self.current_turn = max(
                            math.ceil(self.current_turn) - 1.0, 0.0
                        )
                    else:
                        self.current_turn = max(
                            self.current_turn - 1.0, 0.0
                        )

                if event.key == pygame.K_UP:
                    self.speed += 0.1

                if event.key == pygame.K_DOWN:
                    self.speed = max(0.0, self.speed - 0.1)

                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def _get_zone_color(self, zone: Zone) -> tuple[int, int, int]:
        string = zone.color
        if string == "None":
            return (210, 210, 215)

        color = COLORS.get(string)
        if color is None:
            digested = hashlib.md5(string.encode()).digest()
            color = (digested[0], digested[1], digested[2])
        return color

    def _draw_frame(
            self
    ) -> None:

        self.screen.fill((15, 20, 25))
        zone_radius: float = 20
        drone_radius: float = 5

        # disegno le connessioni
        for connection in self.graph.render_grid.connections:
            start = self.positions.get(connection.zone_a)
            end = self.positions.get(connection.zone_b)
            if start is None or end is None:
                continue

            draw_line(
                surface=self.screen,
                start=start,
                end=end,
                color=(55, 55, 55),
                width=2 * int(drone_radius) + 1
            )

        # disegno le zone
        for zone, position in self.positions.items():
            if zone.zone_type is ZoneType.CONNECTION:
                continue

            color = self._get_zone_color(zone)
            draw_circle(
                surface=self.screen,
                center=position,
                radius=zone_radius,
                color=color
            )

        # disegno i droni
        for drone in self.drones:
            position = self._drone_position(drone)
            if position is None:
                continue

            draw_circle(
                surface=self.screen,
                center=position,
                radius=drone_radius,
                color=(220, 80, 80)
            )

        # disegno i tooltip
        hovered = self._hovered_zone(zone_radius)
        if hovered is not None:
            pos = self.positions.get(hovered)
            if pos is not None:
                lines = [
                    f"HUB: {hovered.name}",
                    f"TYPE: {hovered.zone_type.value}",
                    f"COLOR: {hovered.color}",
                    f"MAX DRONES: {hovered.max_drones}",
                    "",
                    "CONNECTED TO:"
                ]
                neighbors = self._get_neighbors(hovered)
                for z in neighbors:
                    lines.append(f"{z.name}, cost {z.movement_cost()}")
                draw_tooltip(
                    surface=self.screen,
                    screen_size=self.screen.get_size(),
                    lines=lines,
                    pos=pos,
                    font=self.font,
                    color=(242, 242, 242)
                )

        # disegno HUD
        draw_hud(
            surface=self.screen,
            text=f"TURN: {int(self.current_turn)}",
            position=(20, 20),
            font=self.hud_font,
            color=(242, 242, 242)
        )

    def _drone_position(
            self,
            drone: Drone
    ) -> tuple[int, int] | None:

        zone_a = self._position_this_turn(drone)
        zone_b = self._position_next_turn(drone)
        t = self.current_turn - int(self.current_turn)

        if zone_a is None or zone_b is None:
            return None

        zone_a_pos = self.positions.get(zone_a)
        zone_b_pos = self.positions.get(zone_b)

        if zone_a_pos is None or zone_b_pos is None:
            return None

        drones_in_zone = self._get_occupancy(zone_a)

        if zone_a is zone_b:

            if self._later_next_turn(drone) is zone_a:
                waiting_drones = [
                    d for d in drones_in_zone
                    if self._position_next_turn(d) is zone_a
                    and self._later_next_turn(d) is zone_a
                ]
                return self._calculate_orbit(
                    drone=drone,
                    drone_list=waiting_drones,
                    center_x=zone_a_pos[0],
                    center_y=zone_a_pos[1],
                    mult=1.5
                )

            else:
                prepping_drones = [
                    d for d in drones_in_zone
                    if self._position_next_turn(d) is zone_a
                    and self._later_next_turn(d) is not zone_a
                ]
                return self._calculate_orbit(
                    drone=drone,
                    drone_list=prepping_drones,
                    center_x=zone_a_pos[0],
                    center_y=zone_a_pos[1],
                    mult=0.5
                )

        if self.current_turn.is_integer():
            paused_drones = [
                d for d in drones_in_zone
                if self._position_this_turn(d) is not
                self._position_next_turn(d)
            ]
            return self._calculate_orbit(
                drone=drone,
                drone_list=paused_drones,
                center_x=zone_a_pos[0],
                center_y=zone_a_pos[1],
                mult=0.5
            )

        moving_drones = [
            d for d in drones_in_zone
            if self._position_next_turn(d) is
            self._position_next_turn(drone)
        ]

        center_x = int(zone_a_pos[0] + (zone_b_pos[0] - zone_a_pos[0]) * t)
        center_y = int(zone_a_pos[1] + (zone_b_pos[1] - zone_a_pos[1]) * t)

        if len(moving_drones) == 1:
            return (center_x, center_y)

        return self._calculate_orbit(
            drone=drone,
            drone_list=moving_drones,
            center_x=center_x,
            center_y=center_y,
            mult=0.3
        )

    def _hovered_zone(
            self,
            zone_radius: float
            ) -> Zone | None:

        mouse_x, mouse_y = pygame.mouse.get_pos()
        for zone, pos in self.positions.items():
            if zone.zone_type is ZoneType.CONNECTION:
                continue
            rx = mouse_x - pos[0]
            ry = mouse_y - pos[1]
            if math.sqrt(rx*rx + ry*ry) < zone_radius:
                return zone
        return None

    def _get_neighbors(
            self,
            zone: Zone
    ) -> list[Zone]:

        neighbors = []
        for connection in self.graph.render_grid.connections:
            if connection.zone_a is zone:
                neighbors.append(connection.zone_b)
            elif connection.zone_b is zone:
                neighbors.append(connection.zone_a)
        return neighbors

    def _get_occupancy(
            self,
            zone: Zone
    ) -> list[Drone]:

        occupancy: list[Drone] = []
        for drone in self.drones:
            if zone is drone.position_at_turn(int(self.current_turn)):
                occupancy.append(drone)
        return occupancy

    def _calculate_orbit(
            self,
            drone: Drone,
            drone_list: list[Drone],
            center_x: int,
            center_y: int,
            mult: float
    ) -> tuple[int, int]:

        i = drone_list.index(drone)
        angle = (
            self.drone_angles[drone.drone_id]
            + ((2 * math.pi / len(drone_list)) * i)
        )
        orbit_r = self.zone_radius * mult
        x = center_x + int(orbit_r * math.cos(angle))
        y = center_y + int(orbit_r * math.sin(angle))
        return (x, y)

    def _position_this_turn(
            self,
            drone: Drone
    ) -> Zone | None:

        return drone.position_at_turn(int(self.current_turn))

    def _position_next_turn(
            self,
            drone: Drone
    ) -> Zone | None:

        return drone.position_at_turn(int(self.current_turn) + 1)

    def _later_next_turn(
            self,
            drone: Drone
    ) -> Zone | None:

        return drone.position_at_turn(
                math.ceil(self.current_turn + 1)
            )
