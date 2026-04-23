import pygame
Color = tuple[int, int, int]


def draw_circle(
        surface: pygame.Surface,
        center: tuple[int, int],
        radius: int,
        color: Color,
        ) -> None:
    pygame.draw.circle(surface, color, center, radius)


def draw_line(
        surface: pygame.Surface,
        start: tuple[int, int],
        end: tuple[int, int],
        color: Color,
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
        ) -> None:

    text_surface = font.render(text, True, color)
    width, _ = font.size(text)
    centered_position = (
        position[0] - width // 2 + offset[0],
        position[1] + offset[1]
    )
    surface.blit(text_surface, centered_position)


def draw_hud(
        surface: pygame.Surface,
        text: str,
        position: tuple[int, int],
        font: pygame.font.Font,
        color: Color,
        offset: tuple[int, int] = (0, 0)
        ) -> None:

    text_surface = font.render(text, True, color)
    # width, _ = font.size(text)
    centered_position = (
        position[0] + offset[0],
        position[1] + offset[1]
    )
    surface.blit(text_surface, centered_position)


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
    padding = 8

    tooltip_w = max_width + padding * 2
    tooltip_h = line_height * len(lines) + padding * 2

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
        (max_width + padding * 2, line_height * len(lines) + padding * 2),
        pygame.SRCALPHA
    )
    pygame.draw.rect(
        overlay,
        (30, 34, 44, 180),
        overlay.get_rect()
    )
    surface.blit(overlay, (tooltip_x, tooltip_y))

    pygame.draw.rect(
        surface=surface,
        color=(242, 242, 242),
        rect=pygame.Rect(
            tooltip_x, tooltip_y,
            max_width + padding * 2,
            line_height * len(lines) + padding * 2),
        width=3
    )

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        surface.blit(
            text_surface,
            (tooltip_x + padding, tooltip_y + padding + i * line_height)
        )
