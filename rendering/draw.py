import pygame
Color = tuple[int, int, int]


def draw_zone(
        surface: pygame.Surface,
        center: tuple[int, int],
        radius: int,
        color: Color,
) -> None:
    pygame.draw.circle(surface, color, center, radius)


def draw_connection(
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
    width, _ = font.size(text)
    centered_position = (
        position[0] + offset[0],
        position[1] + offset[1]
    )
    surface.blit(text_surface, centered_position)
