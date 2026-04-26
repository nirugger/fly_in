import pygame
import sys
import hashlib
import math
from src.graph import Graph
from src.drone import Drone
from src.zone import Zone, ZoneType
from rendering.data import COLORS, FONT_REGULAR, FONT_BOLD, SPAN, TEXT_COLOR, DRONE_COLOR, RAND_INT
from rendering.draw import (draw_circle,
                            draw_line,
                            draw_label,
                            draw_tooltip,
                            draw_hud,
                            draw_key)


class Renderer:

    def __init__(
            self,
            screen: pygame.Surface,
            graph: Graph,
    ) -> None:

        self.screen = screen
        self.clock = pygame.time.Clock()
        self.graph = graph
        self.drones = self.graph.drones
        self.current_turn: float = 0.0
        self.paused: bool = True
        self.speed: float = 1.0
        self.max_turn = max(
            turn for drone in self.drones
            for turn, _ in drone.path
        )
        self.positions = self._compute_layout()

        h = screen.get_height()
        self.title_font = pygame.font.Font(FONT_BOLD, h // 20)
        self.tooltip_font = pygame.font.Font(FONT_REGULAR, h // 40)
        self.hud_font = pygame.font.Font(FONT_REGULAR, h // 25)
        self.hud_font_bold = pygame.font.Font(FONT_BOLD, h // 25)

        self.drone_angles: dict[int, float] = {
            drone.drone_id: 0.0 for drone in self.drones
        }
        self.zone_radius: float = 20
        self.drone_radius: float = 5
        self.last_int_turn: int = 0
        self.back_to_menu: bool = False
        self.random_color: bool = False
        self.buttons: dict[str, pygame.Rect] = {}

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

        positions: dict[Zone, tuple[int, int]] = {}
        for zone in zones:
            if zone.zone_type is not ZoneType.CONNECTION:
                px, py = raw_positions[zone]
                positions[zone] = (px + dx, py + dy)

        for conn in self.graph.render_grid.connections:
            if conn.zone_c is not None:
                pos_a = positions.get(conn.zone_a)
                pos_b = positions.get(conn.zone_b)
                if pos_a is not None and pos_b is not None:
                    positions[conn.zone_c] = (
                        (pos_a[0] + pos_b[0]) // 2,
                        (pos_a[1] + pos_b[1]) // 2,
                    )

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

            if self.current_turn < 0.0:
                self.current_turn = int(0.0)
                self.speed = 1.0
                self.paused = True

            current_int_turn = int(self.current_turn)
            if self.last_int_turn != current_int_turn:
                self.current_turn = (current_int_turn
                                     if current_int_turn > self.last_int_turn
                                     else self.last_int_turn)
                self.last_int_turn = current_int_turn

            for drone in self.drones:
                self.drone_angles[drone.drone_id] += self.speed * dt * (15 / drone.drones_in_zones)
                # self.drone_angles[drone.drone_id] += self.speed * dt * 2.5

            # current_int_turn = int(self.current_turn)
            # if self.paused is False and self.last_int_turn != current_int_turn:
            if self.speed < 0 and self.paused is False and self.current_turn.is_integer():
                self._reset_drones_sync()
            self._draw_frame()
            pygame.display.flip()

            if self.back_to_menu:
                return

    def _get_zone_color(self, zone: Zone) -> tuple[int, int, int]:
        string = zone.color
        if string == "None":
            return (210, 210, 215)

        color = COLORS.get(string)
        if color is None:
            color = self._get_color_from_string(string)
        return color

    def _get_color_from_string(self, string: str) -> tuple[int, int, int]:
        digested = hashlib.md5(string.encode()).digest()
        color = (digested[0], digested[1], digested[2])
        return color

    def _draw_finish(
            self
    ) -> None:

        cx, cy = (self.screen.get_width() // 2,
                  self.screen.get_height() // 2)

        overlay = pygame.Surface(
            (self.screen.get_width(), self.screen.get_height()),
            pygame.SRCALPHA
        )

        pygame.draw.rect(
            overlay,
            (0, 0, 0, 180),
            overlay.get_rect()
        )

        self.screen.blit(overlay, (0, 0))

        draw_label(
            self.screen,
            "SIMULATION COMPLETE",
            (cx, cy),
            self.title_font,
            TEXT_COLOR,
            (0, 0)
        )

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
                width=2 * int(drone_radius)
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
            drone_pos = self._drone_position(drone)
            if drone_pos is None:
                continue

            color = (
                self._get_color_from_string(
                    str(drone.drone_id + RAND_INT)
                )
                if self.random_color
                else DRONE_COLOR
            )

            draw_circle(
                surface=self.screen,
                center=drone_pos,
                radius=drone_radius,
                color=color
            )

        # disegno i tooltip
        hz = self._hovered_zone(zone_radius)
        if hz is not None and self.current_turn < self.max_turn:
            pos = self.positions.get(hz)
            if pos is not None:
                lines = [
                    f"NAME: {hz.name}",
                    f"TYPE: {hz.zone_type.value}",
                    f"COLOR: {hz.color}",
                    f"MAX DRONES: {hz.max_drones}",
                    "",
                    "NIEGHBORS:"
                ]
                neighbors = self._get_neighbors(hz)
                for z in neighbors:
                    lines.append(f"cost {z.movement_cost()} → {z.name}")
                draw_tooltip(
                    surface=self.screen,
                    screen_size=self.screen.get_size(),
                    lines=lines,
                    pos=pos,
                    font=self.tooltip_font,
                    color=(242, 242, 242)
                )
                # TODO: for zone in neighbors, disegno circonferenza attorno ai neighbors

        # disegno HUD
        draw_hud(
            surface=self.screen,
            text=f"TURN: {int(self.current_turn)}/{self.max_turn}",
            position=(30, 30),
            font=self.title_font,
            color=TEXT_COLOR
        )

        offset, _ = self.title_font.size("KEYS")
        self.buttons['keys'] = draw_key(
            surface=self.screen,
            text="KEYS",
            position=(self.screen.get_width() - offset - 30, 30),
            font=self.title_font,
            color=TEXT_COLOR,
        )

        hb = self._hovered_button()
        if hb is not None:
            rect = self.buttons[hb]
            lines = [
                "↑ : speed up",
                "↓ : speed down",
                "→ : next turn",
                "← : prev turn",
                "C : colors",
                "Q : quit",
                "",
                "SPACE  : pause",
                "ESCAPE : back to menu",
            ]
            draw_tooltip(
                surface=self.screen,
                screen_size=self.screen.get_size(),
                lines=lines,
                pos=rect.topleft,
                font=self.tooltip_font,
                color=(242, 242, 242)
            )

        if self.current_turn >= self.max_turn:
            self.current_turn = float(self.max_turn)
            self.paused = True
            self._draw_finish()

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

                for wd in waiting_drones:
                    wd.drones_in_zones = len(waiting_drones)

                return self._calculate_orbit(
                    drone=drone,
                    drone_list=waiting_drones,
                    center_x=zone_a_pos[0],
                    center_y=zone_a_pos[1],
                    mult=1.5 if len(waiting_drones) > 1 else 2.0,
                    waiting=True if len(waiting_drones) > 1 else False
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

        if (self.current_turn.is_integer() and
                zone_a.zone_type is not ZoneType.CONNECTION):

            print(self.current_turn.is_integer())
            print(self.current_turn)
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

    def _hovered_button(
            self,
            ) -> str | None:

        mx, my = pygame.mouse.get_pos()
        for name, button in self.buttons.items():
            if button.collidepoint(mx, my):
                return name
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
            mult: float,
            waiting: bool = False
    ) -> tuple[int, int]:

        i = drone_list.index(drone)
        angle = (
            self.drone_angles[drone.drone_id]
            + ((2 * math.pi / len(drone_list)) * i)
        )

        orbit_r = self.zone_radius * mult
        if waiting is True:
            orbit_r += drone.orbit_offset
            if drone.max_orbit_reached is False:
                drone.orbit_offset += 1
            else:
                drone.orbit_offset -= 1

            if drone.orbit_offset > SPAN or drone.orbit_offset < 0:
                drone.max_orbit_reached = not drone.max_orbit_reached

            # wating drones rotate counter clockwise
            x = center_x - int(orbit_r * math.cos(angle))

        # if drone.max_orbit_reached is True:
        #     orbit_r = (self.zone_radius * mult) + drone.orbit_offset
        #     drone.orbit_offset += 1
        #     drone.orbit_span_counter += 1
        # else:
        #     orbit_r = (self.zone_radius * mult) + drone.orbit_offset
        #     drone.orbit_offset -= 1
        #     drone.orbit_span_counter += 1

        # if drone.orbit_span_counter >= self.orbit_span:
        #     drone.max_orbit_reached = not drone.max_orbit_reached
        #     drone.orbit_span_counter = 0
        # if drone.orbit_span_counter <= 0:
        #     drone.max_orbit_reached = False

        else:
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

    def _reset_drones_sync(self, orbit: bool = True, angles: bool = True, zones: bool = True) -> None:

        for drone in self.drones:
            if orbit is True:
                drone.orbit_offset = 0
            if angles is True:
                self.drone_angles[drone.drone_id] = self.speed * 0.016 * 2.5
            if zones is True:
                drone.drones_in_zones = 1

    def _handle_events(
            self
    ) -> None:

        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused

                if event.key == pygame.K_RIGHT:

                    self._reset_drones_sync()
                    self.current_turn = min(
                        int(self.current_turn) + 1.0, float(self.max_turn)
                    )

                if event.key == pygame.K_LEFT:

                    # setting orbit offset to 0 to prevent off-sync

                    self.current_turn = max(
                        math.ceil(self.current_turn) - 1.0, 0.0
                    )
                    self._reset_drones_sync()

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

                if event.key == pygame.K_c:
                    self.random_color = not self.random_color

                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
