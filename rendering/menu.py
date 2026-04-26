"""User interface menu for selecting maps and starting the simulation."""

import pygame
from enum import Enum
from rendering.draw import draw_line, draw_label
from rendering.data import MAPS, FONT_REGULAR, FONT_BOLD, COLORS
import sys


class MenuState(Enum):
    """Menu navigation states."""

    MAIN = 1
    CATEGORIES = 2
    MAP_EASY = 3
    MAP_MEDIUM = 4
    MAP_HARD = 5
    MAP_CUSTOM = 6
    INVALID_MAP = 7


class Menu:
    """Handle menu rendering and map selection input."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.center = (self.screen.get_width() // 2,
                       self.screen.get_height() // 2)
        self.title = "FLY IN"
        self.text_color = (242, 242, 242)
        self.state: MenuState = MenuState.MAIN
        self.buttons: dict[str, pygame.Rect] = {}

        self.last_result: str = ""

        self.title_font = pygame.font.Font(FONT_BOLD, 42)
        self.menu_font = pygame.font.Font(FONT_REGULAR, 20)

    def run(self) -> str:
        """Display the menu and return the selected map path.

        The method loops until the user chooses a map or exits the app.

        Returns:
            str: path to the selected map file.
        """
        while True:
            self.screen.fill((5, 10, 15))
            self.buttons.clear()
            self._draw_title()

            if self.state == MenuState.INVALID_MAP:
                self._draw_error()
                self._draw_main_menu()
                # self.state = MenuState.MAIN

            elif self.state == MenuState.MAIN:
                self._draw_main_menu()
            elif self.state == MenuState.CATEGORIES:
                self._draw_categories()
            elif self.state == MenuState.MAP_EASY:
                self._draw_map_easy()
            elif self.state == MenuState.MAP_MEDIUM:
                self._draw_map_medium()
            elif self.state == MenuState.MAP_HARD:
                self._draw_map_hard()
            elif self.state == MenuState.MAP_CUSTOM:
                self._draw_map_custom()
            self._underline_hovered()

            result = self._handle_events()
            if result:
                self.last_result = result
                return result
            pygame.display.flip()

    def _underline_hovered(self) -> None:
        hovered = self._hovered_button()
        if hovered and hovered != "title":
            rect = self.buttons[hovered]
            draw_line(
                surface=self.screen,
                color=self.text_color,
                start=(rect.left, rect.bottom),
                end=(rect.right, rect.bottom),
                width=1
            )

    def _draw_title(self) -> None:
        self.buttons['title'] = draw_label(
            self.screen,
            self.title,
            self.center,
            self.title_font,
            self.text_color,
            (0, -self.menu_font.get_height() * 3)
        )

    def _draw_error(self) -> None:
        draw_label(
            self.screen,
            "[ERROR]: no path was found for this map",
            self.center,
            self.menu_font,
            COLORS['red'],
            (0, -self.menu_font.get_height() - 3)
        )

    def _draw_main_menu(self) -> None:

        self.buttons['start'] = draw_label(
            self.screen,
            "START",
            self.center,
            self.menu_font,
            self.text_color
        )

        self.buttons['exit'] = draw_label(
            self.screen,
            "EXIT",
            self.center,
            self.menu_font,
            self.text_color,
            (0, self.menu_font.get_height() + 3)
        )

    def _draw_categories(self) -> None:

        self.buttons['easy'] = draw_label(
            self.screen,
            "EASY",
            self.center,
            self.menu_font,
            self.text_color
        )

        self.buttons['medium'] = draw_label(
            self.screen,
            "MEDIUM",
            self.center,
            self.menu_font,
            self.text_color,
            (0, self.menu_font.get_height() + 3)
        )

        self.buttons['hard'] = draw_label(
            self.screen,
            "HARD",
            self.center,
            self.menu_font,
            self.text_color,
            (0, (self.menu_font.get_height() + 3) * 2)
        )

        self.buttons['custom'] = draw_label(
            self.screen,
            "CUSTOM",
            self.center,
            self.menu_font,
            self.text_color,
            (0, (self.menu_font.get_height() + 3) * 3)
        )

        self.buttons['back_to_menu'] = draw_label(
            self.screen,
            "BACK",
            self.center,
            self.menu_font,
            self.text_color,
            (0, (self.menu_font.get_height() + 3) * 6)
        )

    def _draw_map_easy(self) -> None:

        self.buttons['title'] = draw_label(
            self.screen,
            self.title,
            self.center,
            self.title_font,
            self.text_color,
            (0, -self.menu_font.get_height() * 3)
        )

        self.buttons['01_e'] = draw_label(
            self.screen,
            "LINEAR PATH",
            self.center,
            self.menu_font,
            self.text_color
        )

        self.buttons['02_e'] = draw_label(
            self.screen,
            "SIMPLE FORK",
            self.center,
            self.menu_font,
            self.text_color,
            (0, self.menu_font.get_height() + 3)
        )

        self.buttons['03_e'] = draw_label(
            self.screen,
            "BASIC CAPACITY",
            self.center,
            self.menu_font,
            self.text_color,
            (0, (self.menu_font.get_height() + 3) * 2)
        )

        self.buttons['back_to_cat'] = draw_label(
            self.screen,
            "BACK",
            self.center,
            self.menu_font,
            self.text_color,
            (0, (self.menu_font.get_height() + 3) * 6)
        )

    def _draw_map_medium(self) -> None:

        self.buttons['title'] = draw_label(
            self.screen,
            self.title,
            self.center,
            self.title_font,
            self.text_color,
            (0, -self.menu_font.get_height() * 3)
        )

        self.buttons['01_m'] = draw_label(
            self.screen,
            "DEAD END TRAP",
            self.center,
            self.menu_font,
            self.text_color
        )

        self.buttons['02_m'] = draw_label(
            self.screen,
            "CIRCULAR LOOP",
            self.center,
            self.menu_font,
            self.text_color,
            (0, self.menu_font.get_height() + 3)
        )

        self.buttons['03_m'] = draw_label(
            self.screen,
            "PRIORITY PUZZLE",
            self.center,
            self.menu_font,
            self.text_color,
            (0, (self.menu_font.get_height() + 3) * 2)
        )

        self.buttons['back_to_cat'] = draw_label(
            self.screen,
            "BACK",
            self.center,
            self.menu_font,
            self.text_color,
            (0, (self.menu_font.get_height() + 3) * 6)
        )

    def _draw_map_hard(self) -> None:

        self.buttons['title'] = draw_label(
            self.screen,
            self.title,
            self.center,
            self.title_font,
            self.text_color,
            (0, -self.menu_font.get_height() * 3)
        )

        self.buttons['01_h'] = draw_label(
            self.screen,
            "MAZE NIGHTMARE",
            self.center,
            self.menu_font,
            self.text_color
        )

        self.buttons['02_h'] = draw_label(
            self.screen,
            "CAPACITY HELL",
            self.center,
            self.menu_font,
            self.text_color,
            (0, self.menu_font.get_height() + 3)
        )

        self.buttons['03_h'] = draw_label(
            self.screen,
            "ULTIMATE CHALLENGE",
            self.center,
            self.menu_font,
            self.text_color,
            (0, (self.menu_font.get_height() + 3) * 2)
        )

        self.buttons['04_h'] = draw_label(
            self.screen,
            "THE IMPOSSIBLE DREAM",
            self.center,
            self.menu_font,
            self.text_color,
            (0, (self.menu_font.get_height() + 3) * 3)
        )

        self.buttons['back_to_cat'] = draw_label(
            self.screen,
            "BACK",
            self.center,
            self.menu_font,
            self.text_color,
            (0, (self.menu_font.get_height() + 3) * 6)
        )

    def _draw_map_custom(self) -> None:

        self.buttons['title'] = draw_label(
            self.screen,
            self.title,
            self.center,
            self.title_font,
            self.text_color,
            (0, -self.menu_font.get_height() * 3)
        )

        self.buttons['01_c'] = draw_label(
            self.screen,
            "RIVER DELTA",
            self.center,
            self.menu_font,
            self.text_color
        )

        self.buttons['02_c'] = draw_label(
            self.screen,
            "FEEDBACK LOOP",
            self.center,
            self.menu_font,
            self.text_color,
            (0, self.menu_font.get_height() + 3)
        )

        self.buttons['03_c'] = draw_label(
            self.screen,
            "HIGHWAY JAM",
            self.center,
            self.menu_font,
            self.text_color,
            (0, (self.menu_font.get_height() + 3) * 2)
        )

        self.buttons['04_c'] = draw_label(
            self.screen,
            "LABYRINTH CITY",
            self.center,
            self.menu_font,
            self.text_color,
            (0, (self.menu_font.get_height() + 3) * 3)
        )

        self.buttons['back_to_cat'] = draw_label(
            self.screen,
            "BACK",
            self.center,
            self.menu_font,
            self.text_color,
            (0, (self.menu_font.get_height() + 3) * 6)
        )

    def _hovered_button(self) -> str | None:
        """Return the name of the button currently under the mouse.

        Returns:
            str | None: button key when hovered, otherwise None.
        """

        mx, my = pygame.mouse.get_pos()
        for name, button in self.buttons.items():
            if button.collidepoint(mx, my):
                return name
        return None

    def _handle_events(self) -> str | None:
        """Process Pygame events and update menu state.

        Returns:
            str | None: selected map path when a map choice is confirmed.
        """

        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN:

                if (event.key == pygame.K_SPACE
                        or event.key == pygame.K_KP_ENTER):
                    pass

                if event.key == pygame.K_UP:
                    pass

                if event.key == pygame.K_DOWN:
                    pass

                if event.key == pygame.K_ESCAPE:
                    if (self.state is MenuState.MAIN or
                            self.state is MenuState.INVALID_MAP):
                        pygame.quit()
                        sys.exit(1)
                    elif self.state is MenuState.CATEGORIES:
                        self.state = MenuState.MAIN
                    elif (self.state is MenuState.MAP_EASY or
                          self.state is MenuState.MAP_MEDIUM or
                          self.state is MenuState.MAP_HARD or
                          self.state is MenuState.MAP_CUSTOM):
                        self.state = MenuState.CATEGORIES

                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:

                # --- easy map choice ----------------------------------------
                if ('easy' in self.buttons and
                        self.buttons['easy'].collidepoint(event.pos)):
                    self.state = MenuState.MAP_EASY

                if ('01_e' in self.buttons and
                        self.buttons['01_e'].collidepoint(event.pos)):
                    return MAPS['01_e']

                if ('02_e' in self.buttons and
                        self.buttons['02_e'].collidepoint(event.pos)):
                    return MAPS['02_e']

                if ('03_e' in self.buttons and
                        self.buttons['03_e'].collidepoint(event.pos)):
                    return MAPS['03_e']

                # --- medium map choice --------------------------------------
                if ('medium' in self.buttons and
                        self.buttons['medium'].collidepoint(event.pos)):
                    self.state = MenuState.MAP_MEDIUM

                if ('01_m' in self.buttons and
                        self.buttons['01_m'].collidepoint(event.pos)):
                    return MAPS['01_m']

                if ('02_m' in self.buttons and
                        self.buttons['02_m'].collidepoint(event.pos)):
                    return MAPS['02_m']

                if ('03_m' in self.buttons and
                        self.buttons['03_m'].collidepoint(event.pos)):
                    return MAPS['03_m']

                # --- hard map choice ----------------------------------------
                if ('hard' in self.buttons and
                        self.buttons['hard'].collidepoint(event.pos)):
                    self.state = MenuState.MAP_HARD

                if ('01_h' in self.buttons and
                        self.buttons['01_h'].collidepoint(event.pos)):
                    return MAPS['01_h']

                if ('02_h' in self.buttons and
                        self.buttons['02_h'].collidepoint(event.pos)):
                    return MAPS['02_h']

                if ('03_h' in self.buttons and
                        self.buttons['03_h'].collidepoint(event.pos)):
                    return MAPS['03_h']

                if ('04_h' in self.buttons and
                        self.buttons['04_h'].collidepoint(event.pos)):
                    return MAPS['04_h']

                # --- custom map choice --------------------------------------
                if ('custom' in self.buttons and
                        self.buttons['custom'].collidepoint(event.pos)):
                    self.state = MenuState.MAP_CUSTOM

                if ('01_c' in self.buttons and
                        self.buttons['01_c'].collidepoint(event.pos)):
                    return MAPS['01_c']

                if ('02_c' in self.buttons and
                        self.buttons['02_c'].collidepoint(event.pos)):
                    return MAPS['02_c']

                if ('03_c' in self.buttons and
                        self.buttons['03_c'].collidepoint(event.pos)):
                    return MAPS['03_c']

                if ('04_c' in self.buttons and
                        self.buttons['04_c'].collidepoint(event.pos)):
                    return MAPS['04_c']

                # --- menu browsing choice -----------------------------------
                if ('start' in self.buttons and
                        self.buttons['start'].collidepoint(event.pos)):
                    self.state = MenuState.CATEGORIES

                if ('back_to_cat' in self.buttons and
                        self.buttons['back_to_cat'].collidepoint(event.pos)):
                    self.state = MenuState.CATEGORIES

                if ('back_to_menu' in self.buttons and
                        self.buttons['back_to_menu'].collidepoint(event.pos)):
                    self.state = MenuState.MAIN

                if ('exit' in self.buttons and
                        self.buttons['exit'].collidepoint(event.pos)):
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        return None
