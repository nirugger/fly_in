import pygame
from rendering.data import TEXT_COLOR
Color = tuple[int, int, int]


def draw_circle(
        surface: pygame.Surface,
        color: Color,
        center: tuple[int, int],
        radius: float,
        width: int = 0,
        edge: bool = False
        ) -> None:
    pygame.draw.circle(surface, color, center, radius, width)
    if edge:
        pygame.draw.circle(surface, (0, 0, 0), center, radius, 2)


def draw_line(
        surface: pygame.Surface,
        color: Color,
        start: tuple[int, int],
        end: tuple[int, int],
        width: int
        ) -> None:
    pygame.draw.line(surface, color, start, end, width)


def draw_label(
        surface: pygame.Surface,
        text: str,
        position: tuple[int, int],
        font: pygame.font.Font,
        color: Color,
        offset: tuple[int, int] = (0, 0)
        ) -> pygame.Rect:

    text_surface = font.render(text, True, color)
    width, height = font.size(text)
    x = position[0] - width // 2 + offset[0]
    y = position[1] - height // 2 + offset[1]
    surface.blit(text_surface, (x, y))
    return pygame.Rect(x, y, width, height)


def draw_hud(
        surface: pygame.Surface,
        text: str,
        position: tuple[int, int],
        font: pygame.font.Font,
        color: Color,
        offset: tuple[int, int] = (0, 0)
        ) -> None:

    text_surface = font.render(text, True, color)
    centered_position = (
        position[0] + offset[0],
        position[1] + offset[1]
    )
    surface.blit(text_surface, centered_position)


def draw_button(
        surface: pygame.Surface,
        text: str,
        position: tuple[int, int],
        font: pygame.font.Font,
        color: Color,
        offset: tuple[int, int] = (0, 0)
        ) -> pygame.Rect:

    text_surface = font.render(text, True, color)
    centered_position = (
        position[0] + offset[0],
        position[1] + offset[1]
    )
    w, h = font.size(text)
    surface.blit(text_surface, centered_position)
    return pygame.Rect(centered_position[0], centered_position[1], w, h)


def draw_tooltip(
        surface: pygame.Surface,
        screen_size: tuple[int, int],
        lines: list[str],
        pos: tuple[int, int],
        font: pygame.font.Font,
        color: Color,
        ) -> None:

    line_height = font.get_linesize()
    max_width = max(font.size(line)[0] for line in lines)
    padding_x = 12
    padding_y = 12

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

    overlay = pygame.Surface(
        (tooltip_w, tooltip_h),
        pygame.SRCALPHA
    )

    pygame.draw.rect(
        overlay,
        (30, 34, 44, 220),
        overlay.get_rect()
    )
    surface.blit(overlay, (tooltip_x, tooltip_y))

    pygame.draw.rect(
        surface=surface,
        color=TEXT_COLOR,
        rect=pygame.Rect(
            tooltip_x, tooltip_y,
            tooltip_w,
            tooltip_h),
        width=2
    )

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        surface.blit(
            text_surface,
            (tooltip_x + padding_x, tooltip_y + padding_y + i * line_height)
        )
