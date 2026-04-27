"""Shared rendering constants and map selection metadata."""

import os
import random

MAPS = {
    '01_e': 'maps/easy/01_linear_path.txt',
    '02_e': 'maps/easy/02_simple_fork.txt',
    '03_e': 'maps/easy/03_basic_capacity.txt',
    '01_m': 'maps/medium/01_dead_end_trap.txt',
    '02_m': 'maps/medium/02_circular_loop.txt',
    '03_m': 'maps/medium/03_priority_puzzle.txt',
    '01_h': 'maps/hard/01_maze_nightmare.txt',
    '02_h': 'maps/hard/02_capacity_hell.txt',
    '03_h': 'maps/hard/03_ultimate_challenge.txt',
    '04_h': 'maps/challenger/01_the_impossible_dream.txt',
    '01_c': 'maps/custom/01_custom_delta_v2.txt',
    '02_c': 'maps/custom/02_feedback_loop_puzzle.txt',
    '03_c': 'maps/custom/03_custom_highway.txt',
    '04_c': 'maps/custom/04_custom_labyrinth_city.txt'
}

SPAN: float = 25.0
RESOLUTION: tuple[int, int] = (1920, 1080)

FONT_DIR: str = os.path.join(os.path.dirname(__file__), 'assets')
FONT_REGULAR: str = os.path.join(FONT_DIR, 'JetBrainsMono-Regular.ttf')
FONT_BOLD: str = os.path.join(FONT_DIR, 'JetBrainsMono-Bold.ttf')

TEXT_COLOR: tuple[int, int, int] = (242, 242, 242)
INVALID_COLOR: tuple[int, int, int] = (110, 110, 120)
DRONE_COLOR: tuple[int, int, int] = (220, 110, 110)

MIN_INT: int = -2147483648
MAX_INT: int = 2147483647
RAND_INT: int = random.randint(MIN_INT, MAX_INT)

COLORS: dict[str, tuple[int, int, int]] = {
    # --- Original colors, darkened ---
    "red": (210, 80, 90),
    "green": (80, 175, 90),
    "blue": (70, 130, 210),
    "orange": (220, 140, 50),
    "yellow": (210, 190, 50),
    "purple": (150, 80, 210),
    "cyan": (60, 190, 195),
    "pink": (220, 90, 170),
    "lime": (120, 205, 70),
    "brown": (140, 100, 60),
    "magenta": (195, 60, 180),
    "gold": (205, 165, 30),
    "violet": (120, 80, 220),
    "crimson": (185, 30, 55),
    "maroon": (140, 40, 55),
    "default": (140, 140, 150),

    # --- Reds & Pinks ---
    "rose": (195, 50, 100),
    "coral": (210, 90, 70),
    "salmon": (200, 100, 85),
    "ruby": (155, 15, 40),
    "scarlet": (195, 25, 35),
    "raspberry": (160, 30, 80),
    "blush": (190, 80, 110),

    # --- Oranges & Yellows ---
    "amber": (200, 130, 20),
    "ochre": (175, 130, 30),
    "mustard": (185, 155, 25),
    "bronze": (160, 105, 35),
    "peach": (210, 130, 90),
    "tangerine": (220, 115, 30),
    "saffron": (210, 165, 20),

    # --- Greens ---
    "teal": (30, 150, 140),
    "olive": (110, 130, 40),
    "forest": (35, 115, 50),
    "sage": (100, 145, 90),
    "emerald": (20, 155, 85),
    "mint": (50, 170, 130),
    "jade": (40, 140, 100),
    "moss": (90, 120, 50),
    "chartreuse": (140, 190, 25),
    "fern": (80, 135, 65),

    # --- Blues ---
    "navy": (25, 55, 140),
    "cobalt": (35, 85, 190),
    "sky": (60, 150, 210),
    "steel": (70, 110, 160),
    "indigo": (65, 50, 180),
    "slate": (80, 100, 140),
    "azure": (30, 120, 195),
    "denim": (75, 105, 160),
    "sapphire": (20, 70, 170),
    "midnight": (20, 30, 110),

    # --- Purples & Magentas ---
    "lavender": (130, 90, 195),
    "plum": (130, 50, 130),
    "grape": (110, 40, 155),
    "orchid": (175, 60, 175),
    "mauve": (155, 90, 155),
    "fuchsia": (185, 25, 155),
    "lilac": (145, 90, 200),
    "amethyst": (130, 70, 185),
    "mulberry": (140, 40, 110),
    "wisteria": (140, 100, 190),

    # --- Neutrals & Metallics ---
    "white": (230, 230, 230),
    "silver": (170, 170, 180),
    "gray": (110, 110, 120),
    "charcoal": (65, 65, 75),
    "black": (30, 30, 35),
    "ivory": (220, 210, 185),
    "sand": (195, 175, 130),
    "tan": (180, 150, 100),
    "khaki": (165, 150, 85),
    "beige": (200, 185, 155),
    "copper": (175, 100, 55),
    "pewter": (130, 130, 145),
    "iron": (90, 90, 100),

    # --- Special / Exotic ---
    "turquoise": (30, 175, 160),
    "aqua": (25, 185, 175),
    "sienna": (160, 85, 40),
    "terracotta": (185, 90, 60),
    "rust": (170, 75, 40),
    "burgundy": (120, 25, 45),
    "garnet": (145, 30, 50),
    "mahogany": (130, 55, 35),
    "chocolate": (115, 65, 30),
    "caramel": (185, 120, 45),
    "lemon": (210, 195, 30),
    "cream": (215, 200, 155),
    "smoke": (150, 150, 165),
    "ash": (160, 155, 160),
    "pine": (40, 100, 60),
    "spruce": (35, 85, 70),
    "dusk": (100, 80, 130),
    "dawn": (195, 130, 110),
    "storm": (70, 80, 110),
    "ocean": (25, 100, 160),
    "lagoon": (25, 155, 155),
    "lava": (200, 55, 20),
    "sand_dark": (170, 145, 90),
    "parchment": (195, 175, 120),
    "obsidian": (35, 30, 45),

    # --- Highlight ---
    "highlight_hovered": (240, 240, 255),
    "highlight_blocked": (220,  50,  60),
    "highlight_restricted": (230, 185,  30),
    "highlight_priority": (80, 215,  90),
    "highlight_normal": (60, 175, 230),
}
