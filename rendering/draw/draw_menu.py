"""Menu drawing helpers for the Fly In interface."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rendering.menu import Menu

from rendering.draw.draw_templates import draw_label
from rendering.utils.tools import get_random_color
from rendering.utils.mousehover import h_button

from rendering.data import TEXT_COLOR, MAPS, COLORS, INVALID_COLOR

import pygame


def title(menu: Menu) -> None:
    """Render the main menu title."""
    height = menu.menu_font.get_height()
    menu.buttons['title'] = draw_label(
        menu.screen, "FLY IN", menu.center,
        menu.title_font, TEXT_COLOR,
        offset=(0, -(height * 3))
        )


def error_msg(menu: Menu) -> None:
    """Render an error message when no valid map can be selected."""
    draw_label(menu.screen, "[ERROR]: no path was found for this map",
               menu.center, menu.menu_font, COLORS['red'],
               offset=(0, -(menu.y_off)))


def draw_back(menu: Menu) -> pygame.Rect:
    """Render the back button and return its bounds."""
    return draw_label(
        menu.screen, "BACK", menu.center, menu.menu_font, TEXT_COLOR,
        offset=(0, menu.y_off * 6)
        )


def main_menu(menu: Menu) -> None:
    """Render the main menu options."""
    menu.buttons['start'] = draw_label(
        menu.screen, "START", menu.center, menu.menu_font, TEXT_COLOR
        )

    menu.buttons['exit'] = draw_label(
        menu.screen, "EXIT", menu.center, menu.menu_font, TEXT_COLOR,
        offset=(0, menu.y_off)
        )


def categories(menu: Menu) -> None:
    """Render the map category selection screen."""
    menu.buttons['easy'] = draw_label(
        menu.screen, "EASY", menu.center, menu.menu_font, TEXT_COLOR
        )

    menu.buttons['medium'] = draw_label(
        menu.screen, "MEDIUM", menu.center, menu.menu_font, TEXT_COLOR,
        offset=(0, menu.y_off)
        )

    menu.buttons['hard'] = draw_label(
        menu.screen, "HARD", menu.center, menu.menu_font, TEXT_COLOR,
        offset=(0, (menu.y_off) * 2)
        )

    menu.buttons['custom'] = draw_label(
        menu.screen, "CUSTOM", menu.center, menu.menu_font, TEXT_COLOR,
        offset=(0, menu.y_off * 3)
        )

    menu.buttons['back_to_menu'] = draw_back(menu)


def map_easy(menu: Menu) -> None:
    """Render the easy maps selection screen."""
    rect = draw_label(
        menu.screen, "LINEAR PATH", menu.center, menu.menu_font,
        TEXT_COLOR if MAPS['01_e'] not in menu.x_maps else INVALID_COLOR
        )
    if MAPS['01_e'] not in menu.x_maps:
        menu.buttons['01_e'] = rect

    rect = draw_label(
        menu.screen, "SIMPLE FORK", menu.center, menu.menu_font,
        TEXT_COLOR if MAPS['02_e'] not in menu.x_maps else INVALID_COLOR,
        offset=(0, menu.y_off)
        )
    if MAPS['02_e'] not in menu.x_maps:
        menu.buttons['02_e'] = rect

    rect = draw_label(
        menu.screen, "BASIC CAPACITY", menu.center, menu.menu_font,
        TEXT_COLOR if MAPS['03_e'] not in menu.x_maps else INVALID_COLOR,
        offset=(0, menu.y_off * 2)
        )
    if MAPS['03_e'] not in menu.x_maps:
        menu.buttons['03_e'] = rect

    menu.buttons['back_to_cat'] = draw_back(menu)


def map_medium(menu: Menu) -> None:
    """Render the medium maps selection screen."""
    rect = draw_label(
        menu.screen, "DEAD END TRAP", menu.center, menu.menu_font,
        TEXT_COLOR if MAPS['01_m'] not in menu.x_maps else INVALID_COLOR
        )
    if MAPS['01_m'] not in menu.x_maps:
        menu.buttons['01_m'] = rect

    rect = draw_label(
        menu.screen, "CIRCULAR LOOP", menu.center, menu.menu_font,
        TEXT_COLOR if MAPS['02_m'] not in menu.x_maps else INVALID_COLOR,
        offset=(0, menu.y_off)
        )
    if MAPS['02_m'] not in menu.x_maps:
        menu.buttons['02_m'] = rect

    rect = draw_label(
        menu.screen, "PRIORITY PUZZLE", menu.center, menu.menu_font,
        TEXT_COLOR if MAPS['03_m'] not in menu.x_maps else INVALID_COLOR,
        offset=(0, menu.y_off * 2)
        )
    if MAPS['03_m'] not in menu.x_maps:
        menu.buttons['03_m'] = rect

    menu.buttons['back_to_cat'] = draw_back(menu)


def map_hard(menu: Menu) -> None:
    """Render the hard maps selection screen."""
    rect = draw_label(
        menu.screen, "MAZE NIGHTMARE", menu.center, menu.menu_font,
        TEXT_COLOR if MAPS['01_h'] not in menu.x_maps else INVALID_COLOR
        )
    if MAPS['01_h'] not in menu.x_maps:
        menu.buttons['01_h'] = rect

    rect = draw_label(
        menu.screen, "CAPACITY HELL", menu.center, menu.menu_font,
        TEXT_COLOR if MAPS['02_h'] not in menu.x_maps else INVALID_COLOR,
        offset=(0, menu.y_off)
        )
    if MAPS['02_h'] not in menu.x_maps:
        menu.buttons['02_h'] = rect

    rect = draw_label(
        menu.screen, "ULTIMATE CHALLENGE", menu.center, menu.menu_font,
        TEXT_COLOR if MAPS['03_h'] not in menu.x_maps else INVALID_COLOR,
        offset=(0, menu.y_off * 2)
        )
    if MAPS['03_h'] not in menu.x_maps:
        menu.buttons['03_h'] = rect

    rect = draw_label(
        menu.screen, "THE IMPOSSIBLE DREAM", menu.center, menu.menu_font,
        TEXT_COLOR if MAPS['04_h'] not in menu.x_maps else INVALID_COLOR,
        offset=(0, menu.y_off * 3)
        )
    if MAPS['04_h'] not in menu.x_maps:
        menu.buttons['04_h'] = rect

    menu.buttons['back_to_cat'] = draw_back(menu)


def map_custom(menu: Menu) -> None:
    """Render the custom maps selection screen."""
    rect = draw_label(
        menu.screen, "HIGHWAY JAM", menu.center, menu.menu_font,
        TEXT_COLOR if MAPS['01_c'] not in menu.x_maps else INVALID_COLOR
        )
    if MAPS['01_c'] not in menu.x_maps:
        menu.buttons['01_c'] = rect

    rect = draw_label(
        menu.screen, "FEEDBACK LOOP", menu.center, menu.menu_font,
        TEXT_COLOR if MAPS['02_c'] not in menu.x_maps else INVALID_COLOR,
        offset=(0, menu.y_off)
        )
    if MAPS['02_c'] not in menu.x_maps:
        menu.buttons['02_c'] = rect

    rect = draw_label(
        menu.screen, "LABYRINTH CITY", menu.center, menu.menu_font,
        TEXT_COLOR if MAPS['03_c'] not in menu.x_maps else INVALID_COLOR,
        offset=(0, menu.y_off * 2)
        )
    if MAPS['03_c'] not in menu.x_maps:
        menu.buttons['03_c'] = rect

    rect = draw_label(
        menu.screen, "A DAY OFF", menu.center, menu.menu_font,
        TEXT_COLOR if MAPS['04_c'] not in menu.x_maps else INVALID_COLOR,
        offset=(0, menu.y_off * 3)
        )
    if MAPS['04_c'] not in menu.x_maps:
        menu.buttons['04_c'] = rect

    menu.buttons['back_to_cat'] = draw_back(menu)


def underline_hovered(
        menu: Menu,
        random_color: bool = False,
        ) -> None:
    """Underline the menu item currently under the mouse cursor."""
    special_color = get_random_color() if random_color else TEXT_COLOR
    hovered = h_button(menu)
    if hovered and hovered != "title":
        rect = menu.buttons[hovered]
        pygame.draw.line(menu.screen, special_color,
                         rect.bottomleft, rect.bottomright)
