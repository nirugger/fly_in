"""Drawing helper functions for the Pygame renderer."""

from rendering.data import TEXT_COLOR, CONN_W, ZONE_R, CONN_COLOR
from rendering.utils import get_random_color

import pygame
import math

Color = tuple[int, int, int]


def draw_circle(
        surface: pygame.Surface,
        color: Color,
        center: tuple[int, int],
        radius: float,
        width: int = 0,
        edge: bool = False
        ) -> None:
    """Draw a circle on the target surface.

    Args:
        surface (pygame.Surface): rendering surface.
        color (Color): fill colour for the circle.
        center (tuple[int, int]): circle center coordinates.
        radius (float): circle radius.
        width (int): line width, zero for filled circle.
        edge (bool): when True, draw a black outline.
    """
    pygame.draw.circle(surface, color, center, radius, width)
    if edge:
        pygame.draw.circle(surface, (0, 0, 0), center, radius, 2)


def draw_connection(
        surface: pygame.Surface,
        start: tuple[int, int],
        end: tuple[int, int],
        width: int = CONN_W,
        color: tuple[int, int, int] = CONN_COLOR,
        ) -> tuple[tuple[int, int], tuple[int, int]]:

    x1, y1 = start
    x2, y2 = end

    angle = math.atan2(abs(y2 - y1), abs(x2 - x1))

    if x2 > x1:
        nx1 = x1 + math.cos(angle) * ZONE_R
        nx2 = x2 - math.cos(angle) * ZONE_R
    else:
        nx1 = x1 - math.cos(angle) * ZONE_R
        nx2 = x2 + math.cos(angle) * ZONE_R

    if y2 > y1:
        ny1 = y1 + math.sin(angle) * ZONE_R
        ny2 = y2 - math.sin(angle) * ZONE_R
    else:
        ny1 = y1 - math.sin(angle) * ZONE_R
        ny2 = y2 + math.sin(angle) * ZONE_R

    n_start = (int(nx1), int(ny1))
    n_end = (int(nx2), int(ny2))

    pygame.draw.line(surface, color, n_start, n_end, width)
    return (n_start, n_end)


def draw_hovered_connection(
        surface: pygame.Surface,
        start: tuple[int, int],
        end: tuple[int, int],
        width: int = CONN_W,
        color: tuple[int, int, int] = TEXT_COLOR
        ) -> None:

    pygame.draw.circle(surface, color,
                       start, ZONE_R + 2, width)

    pygame.draw.circle(surface, color,
                       end, ZONE_R + 2, width)

    draw_connection(surface, start, end,
                    width, color)


def draw_line(
        surface: pygame.Surface,
        color: Color,
        start: tuple[int, int],
        end: tuple[int, int],
        width: int
        ) -> None:
    """Draw a line on the target surface.

    Args:
        surface (pygame.Surface): rendering surface.
        color (Color): line colour.
        start (tuple[int, int]): start coordinates.
        end (tuple[int, int]): end coordinates.
        width (int): line thickness.
    """
    pygame.draw.line(surface, color, start, end, width)


def draw_arc(
        surface: pygame.Surface,
        center: tuple[int, int],
        radius: float,
        connection_point: tuple[int, int],
        color: tuple[int, int, int] = (255, 0, 0)
        ) -> None:

    cx, cy = center
    px, py = connection_point

    arc_angle = math.atan2(abs(py - cy), abs(px - cx))
    span = math.radians(45)
    start_angle = arc_angle + span
    end_angle = arc_angle - span

    rect = pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2)

    pygame.draw.arc(surface, color, rect, start_angle, end_angle, CONN_W)


def draw_label(
        surface: pygame.Surface,
        text: str,
        position: tuple[int, int],
        font: pygame.font.Font,
        color: Color,
        offset: tuple[int, int] = (0, 0),
        is_info: bool = False
        ) -> pygame.Rect:
    """Render centered text and return its bounding rect.

    Args:
        surface (pygame.Surface): surface to draw on.
        text (str): text to render.
        position (tuple[int, int]): center position for the label.
        font (pygame.font.Font): font for rendering.
        color (Color): text color.
        offset (tuple[int, int], optional): pixel offset from center.

    Returns:
        pygame.Rect: bounding rectangle of the rendered label.
    """
    text_surface = font.render(text, True, color)
    width, height = font.size(text)
    x = position[0] - width // 2 + offset[0]
    y = position[1] - height // 2 + offset[1]
    surface.blit(text_surface, (x, y))
    if is_info:
        x -= 15
        y -= 4
        width += 40
        height += 16
    return pygame.Rect(x, y, width, height)


def draw_hud(
        surface: pygame.Surface,
        text: str,
        position: tuple[int, int],
        font: pygame.font.Font,
        color: Color,
        offset: tuple[int, int] = (0, 0)
        ) -> None:
    """Render HUD text at a specified position.

    Args:
        surface (pygame.Surface): render target.
        text (str): text to display.
        position (tuple[int, int]): top-left reference position.
        font (pygame.font.Font): font for rendering.
        color (Color): text color.
        offset (tuple[int, int], optional): pixel offset from 'position'.
    """
    text_surface = font.render(text, True, color)
    centered_position = (
        position[0] + offset[0],
        position[1] + offset[1]
    )
    surface.blit(text_surface, centered_position)


def draw_button(
        surface: pygame.Surface,
        color: Color,
        font: pygame.font.Font,
        lines: list[str],
        pos: tuple[int, int],
        interline: int = 0,
        offset: tuple[int, int] = (0, 0),
        frame: bool = False
        ) -> pygame.Rect:
    """Render a button label and return its bounding rectangle.

    Args:
        surface (pygame.Surface): surface to draw on.
        text (str): label text.
        position (tuple[int, int]): upper-left base position.
        font (pygame.font.Font): font to use.
        color (Color): text color.
        offset (tuple[int, int], optional): translation offset.

    Returns:
        pygame.Rect: rectangle containing the rendered button text.
    """
    line_height = font.get_linesize() + interline
    max_width = max(font.size(line)[0] for line in lines)
    padding_x = 0
    padding_y = 0

    tooltip_w = max_width + padding_x * 2
    tooltip_h = line_height * len(lines) + padding_y * 2

    screen_size = surface.get_size()
    screen_cx = screen_size[0] // 2
    if pos[0] > screen_cx:
        tooltip_x = pos[0] - tooltip_w
    else:
        tooltip_x = pos[0]

    screen_cy = screen_size[1] // 2
    if pos[1] < screen_cy:
        tooltip_y = pos[1]
    else:
        tooltip_y = pos[1] - tooltip_h

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, TEXT_COLOR)
        surface.blit(
            text_surface,
            (tooltip_x + offset[0] + padding_x,
             tooltip_y + offset[1] + padding_y + i * line_height)
        )

    left = tooltip_x + offset[0] - 15
    top = tooltip_y + offset[1]
    width = float(tooltip_w + 30)
    height = float(tooltip_h - interline)

    if frame is True:
        pygame.draw.rect(surface, color,
                         pygame.Rect(left, top, width, height),
                         width=3, border_radius=10)

    return pygame.Rect(left, top, width, height)


def draw_tooltip(
        surface: pygame.Surface,
        color: Color,
        font: pygame.font.Font,
        lines: list[str],
        pos: tuple[int, int],
        is_info: bool = False
        ) -> None:
    """Draw a tooltip box with multiple lines of text.

    Args:
        surface (pygame.Surface): surface to draw on.
        screen_size (tuple[int, int]): size of the screen in pixels.
        lines (list[str]): tooltip text lines.
        pos (tuple[int, int]): preferred tooltip origin.
        font (pygame.font.Font): font for tooltip text.
        color (Color): text color.
    """
    line_height = font.get_linesize()
    max_width = max(font.size(line)[0] for line in lines)
    padding_x = 12
    padding_y = 12

    screen_size = surface.get_size()
    tooltip_w = max_width + padding_x * 2
    tooltip_h = line_height * len(lines) + padding_y * 2

    screen_cx = screen_size[0] // 2
    if pos[0] > screen_cx:
        tooltip_x = pos[0] - tooltip_w
    else:
        tooltip_x = pos[0]

    screen_cy = screen_size[1] // 2
    if pos[1] < screen_cy:
        tooltip_y = pos[1]
    else:
        tooltip_y = pos[1] - tooltip_h

    overlay = pygame.Surface((tooltip_w, tooltip_h), pygame.SRCALPHA)

    pygame.draw.rect(overlay, (30, 34, 44, 220), overlay.get_rect(), 0,
                     border_top_left_radius=10,
                     border_top_right_radius=-1 if is_info else 10,
                     border_bottom_left_radius=10,
                     border_bottom_right_radius=10
                     )
    surface.blit(overlay, (tooltip_x, tooltip_y))

    pygame.draw.rect(surface, color,
                     pygame.Rect(tooltip_x, tooltip_y, tooltip_w, tooltip_h),
                     width=2,
                     border_top_left_radius=10,
                     border_top_right_radius=-1 if is_info else 10,
                     border_bottom_left_radius=10,
                     border_bottom_right_radius=10
                     )

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, TEXT_COLOR)
        surface.blit(
            text_surface,
            (tooltip_x + padding_x, tooltip_y + padding_y + i * line_height)
        )


def draw_finish(
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

    frame = draw_label(screen, "SIMULATION COMPLETE", (cx, cy),
                       font, color)

    pygame.draw.line(
        screen, color, frame.bottomleft, frame.bottomright, CONN_W
    )
